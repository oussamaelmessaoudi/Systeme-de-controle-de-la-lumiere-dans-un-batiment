import asyncio
import json
import psycopg2


DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "Hamdi2002",
    "host": "localhost",
    "port": "5432"
}

old_gpio_set = set()

async def update_diagram(gpios):
    with open("diagram.json", "r", encoding="utf-8") as f:
        diagram = json.load(f)

    diagram["parts"] = [p for p in diagram["parts"] if not p["id"].startswith("led") and not p["id"].startswith("r")]
    diagram["connections"] = [c for c in diagram["connections"] if not any(x.startswith("led") or x.startswith("r") for x in (c[0], c[1]))]

    left_base = -100
    top_pos = 50
    spacing = 60

    for i, gpio in enumerate(gpios):
        led_id = f"led{i+1}"
        resistor_id = f"r{i+1}"
        left_pos = left_base + i * spacing

        diagram["parts"].append({
            "type": "wokwi-led",
            "id": led_id,
            "top": top_pos,
            "left": left_pos,
            "attrs": {"color": "red"}
        })

        diagram["parts"].append({
            "type": "wokwi-resistor",
            "id": resistor_id,
            "top": top_pos + 60,
            "left": left_pos + 30,
            "attrs": {"value": "220"}
        })

        diagram["connections"].append([f"{resistor_id}:2", f"esp:{gpio}", "green", []])
        diagram["connections"].append([f"{resistor_id}:1", f"{led_id}:A", "green", []])
        diagram["connections"].append([f"{led_id}:C", "gnd1:GND", "black", []])

    with open("diagram.json", "w", encoding="utf-8") as f:
        json.dump(diagram, f, indent=2)
    print("diagram.json updated with", len(gpios), "LED(s).")

async def fetch_gpio_pins():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT led_pin FROM users")
            return sorted(row[0] for row in cur.fetchall())

async def check_for_changes():
    global old_gpio_set
    while True:
        try:
            new_gpios = await fetch_gpio_pins()
            new_gpio_set = set(new_gpios)
            if new_gpio_set != old_gpio_set:
                await update_diagram(new_gpios)
                old_gpio_set = new_gpio_set
        except Exception as e:
            print("Database polling error:", e)
        await asyncio.sleep(5)

async def main():
    print("Starting diagram updater...")
    await check_for_changes()

if __name__ == "__main__":
    asyncio.run(main())
