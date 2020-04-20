# Generated by Django 3.0.5 on 2020-04-20 14:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0002_thing_credentials_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThingRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule', models.CharField(max_length=1000)),
                ('thing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rules', to='things.Thing')),
            ],
        ),
    ]
