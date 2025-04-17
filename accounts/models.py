from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'accounts_profile'

    def __str__(self):
        return f"{self.user.username}'s profile"

# Create Profile when User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

# Save Profile when User is updated
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)

# Ensure signals are connected
def ready():
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)

class BPRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bp_records")
    date = models.DateField()
    systolic = models.PositiveIntegerField()
    diastolic = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.user.username} - {self.date}"


class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    content = models.TextField()

    def __str__(self):
        return f"Journal Entry for {self.user.username} on {self.date}"

