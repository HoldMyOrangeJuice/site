# Generated by Django 2.2.7 on 2019-11-27 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0005_auto_20191127_1105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='price',
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.TextField(blank=True),
        ),
    ]