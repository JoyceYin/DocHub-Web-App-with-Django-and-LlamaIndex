# Generated by Django 4.2.11 on 2024-04-01 21:38

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("document", "0003_querydb_sumdb_delete_filedb_querydb_doc_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="querydb",
            name="sum_content",
        ),
    ]
