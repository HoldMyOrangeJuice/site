# Generated by Django 2.2.7 on 2019-12-29 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0003_item_category_to_search'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='index',
            field=models.TextField(blank=True, null=None),
        ),
    ]
