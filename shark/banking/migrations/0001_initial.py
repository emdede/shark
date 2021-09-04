# Generated by Django 3.2.7 on 2021-09-04 17:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='account name')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_date', models.DateField(verbose_name='entry date')),
                ('value_date', models.DateField(verbose_name='value date')),
                ('text_key', models.CharField(max_length=100)),
                ('primanota', models.CharField(max_length=100)),
                ('account_holder', models.CharField(max_length=100)),
                ('account_number', models.CharField(max_length=100)),
                ('bank_code', models.CharField(max_length=100)),
                ('reference', models.TextField(max_length=100)),
                ('currency', models.CharField(default='EUR', max_length=3)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=11)),
                ('debit_credit', models.CharField(max_length=2)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='banking.account')),
            ],
        ),
    ]
