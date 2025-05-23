# Generated by Django 5.2.1 on 2025-05-13 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_analytics'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='analytics',
            name='core_analyt_zone_id_11de12_idx',
        ),
        migrations.RemoveField(
            model_name='analytics',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='analytics',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='analytics',
            name='zone',
        ),
        migrations.AddField(
            model_name='analytics',
            name='zone_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterModelTable(
            name='analytics',
            table='core_analytics',
        ),
    ]
