# Generated by Django 4.2.11 on 2024-04-03 00:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("document", "0006_rename_sumdb_filedb_delete_querydb"),
    ]

    operations = [
        migrations.AddField(
            model_name="filedb",
            name="keyword",
            field=models.CharField(default="None", max_length=150),
            preserve_default=False,
        ),
    ]
