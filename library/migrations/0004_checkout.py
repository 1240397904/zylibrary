# Generated by Django 2.2.5 on 2019-09-24 08:02

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import library.models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0003_auto_20190924_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckOut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(2, '有效'), (-2, '无效')], default=2, verbose_name='状态')),
                ('create_user_id', models.IntegerField(editable=False, null=True, verbose_name='创建用户')),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='新建时间')),
                ('update_user_id', models.IntegerField(editable=False, null=True, verbose_name='更新用户')),
                ('update_time', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='更新时间')),
                ('book_status', models.CharField(choices=[('ON', 'On Shelf'), ('OUT', 'Check Out'), ('RE', 'Returned'), ('LO', 'Lost')], default='ON', max_length=10, verbose_name='书籍状态')),
                ('time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='借阅时间')),
                ('type', models.CharField(choices=[('SC', 'Scan Code'), ('SH', 'Shift')], default='SC', max_length=2, verbose_name='Type')),
                ('return_date', models.DateField(default=library.models.calc_return_date, verbose_name='归还日期')),
                ('returned_time', models.DateTimeField(blank=True, null=True, verbose_name='归还时间')),
                ('allow_shift', models.BooleanField(default=True, verbose_name='Allow Shift')),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='library.Book', verbose_name='书名')),
                ('user_profile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='library.UserProfile', verbose_name='用户')),
            ],
            options={
                'verbose_name': '借阅',
                'verbose_name_plural': '借阅',
            },
        ),
    ]
