# Generated by Django 3.0.7 on 2020-12-30 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('synchronizer', '0006_plreservation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='date',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='doctor',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='duration_minutes',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='patient',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='po_id',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='zl_id',
        ),
        migrations.AddField(
            model_name='reservation',
            name='email',
            field=models.CharField(default='test@test.pl', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='end_time',
            field=models.DateTimeField(default='2020-02-03 09:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='first_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='last_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='pl_reservation_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='pl_resource_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='start_time',
            field=models.DateTimeField(default='2020-02-03 09:00:00'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='zl_address_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='zl_doctor_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='zl_facility_id',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='zl_resource_id',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
