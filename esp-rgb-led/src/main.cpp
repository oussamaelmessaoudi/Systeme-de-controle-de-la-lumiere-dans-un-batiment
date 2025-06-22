#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>


const char* ssid = "Wokwi-GUEST";
const char* password = "";

WebServer server(80); 

void handleRpc() {
  if (server.method() != HTTP_POST) {
    server.send(405, "text/plain", "Method Not Allowed");
    return;
  }

  String requestBody = server.arg("plain");
  Serial.println("--> Received RPC request: " + requestBody);

  JsonDocument doc;
  DeserializationError error = deserializeJson(doc, requestBody);

  if (error) {
    server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
    return;
  }

  if (doc.containsKey("method") && strcmp(doc["method"], "set_led") == 0) {
    int pin = doc["params"]["pin"];
    bool state = doc["params"]["state"];

    Serial.printf("Controlling PIN %d -> State %s\n", pin, state ? "ON" : "OFF");

    pinMode(pin, OUTPUT);
    digitalWrite(pin, state ? HIGH : LOW);

    server.send(200, "application/json", "{\"jsonrpc\":\"2.0\",\"result\":\"OK\"}");
  } else {
    server.send(400, "application/json", "{\"error\":\"Invalid RPC call\"}");
  }
}

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wokwi WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  server.on("/rpc", handleRpc);
  server.begin();
  Serial.println("HTTP server started. Listening for RPC calls on /rpc");
}

void loop() {
  server.handleClient();
}


