from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import cloudinary.models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ('socialmediaapp', '0034_delete_loggedinaccount'),  # هذا هو السطر المعدل الصحيح
]


    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=10, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_families', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='families', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FamilyPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image')),
                ('audio', models.FileField(blank=True, null=True, upload_to='audio/')),
                ('video', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, resource_type='video', verbose_name='video')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('family', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='socialmediaapp.family')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('likers', models.ManyToManyField(blank=True, related_name='family_likes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
