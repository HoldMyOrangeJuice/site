# Generated by Django 2.2.7 on 2019-12-29 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_item_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='index',
            field=models.IntegerField(blank=True, null=None),
        ),
    ]
