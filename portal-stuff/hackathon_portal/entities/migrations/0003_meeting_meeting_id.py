# Generated by Django 2.2 on 2019-04-04 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20190404_0741'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='meeting_id',
            field=models.UUIDField(default='2755772e-365d-4f6b-8a0e-649fa259abd1', editable=False),
            preserve_default=False,
        ),
    ]