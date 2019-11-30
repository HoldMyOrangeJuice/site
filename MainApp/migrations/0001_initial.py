# Generated by Django 2.2.7 on 2019-11-29 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=None)),
                ('name_to_search', models.TextField(blank=True, null=None)),
                ('amount', models.TextField(blank=True, null=None)),
                ('price', models.TextField(blank=True, null=None)),
                ('year', models.TextField(blank=True, null=None)),
                ('category', models.TextField(blank=True, null=None)),
                ('to_show', models.BooleanField(blank=True, null=None)),
            ],
        ),
    ]
