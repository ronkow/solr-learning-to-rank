# Generated by Django 2.0.13 on 2020-10-03 08:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('appquiz', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelQuestionbank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qb_question', models.TextField(unique=True)),
                ('qb_answer', models.CharField(max_length=50)),
                ('qb_choice1', models.CharField(max_length=50)),
                ('qb_choice2', models.CharField(max_length=50)),
                ('qb_choice3', models.CharField(max_length=50)),
                ('qb_topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modelqbtopic', to='appquiz.ModelTopic')),
            ],
        ),
    ]