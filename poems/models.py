from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name


GENRE_CHOICES = [
    ('love', 'Love'),
    ('nature', 'Nature'),
    ('life', 'Life'),
    ('sadness', 'Sadness'),
    ('hope', 'Hope'),
    ('humor', 'Humor'),
    ('spiritual', 'Spiritual'),
    ('other', 'Other'),
]


class Poem(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='poems')
    title = models.CharField(max_length=200)
    content = models.TextField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'"{self.title}" by {self.author.name}'

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def comment_count(self):
        return self.comments.count()


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'poem')

    def __str__(self):
        return f'{self.user.name} liked "{self.poem.title}"'


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    poem = models.ForeignKey(Poem, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.name} on "{self.poem.title}"'


# ─── Messaging ─────────────────────────────────────────────────────────────────

class Conversation(models.Model):
    """DM thread between exactly 2 users."""
    participants = models.ManyToManyField(CustomUser, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        names = ', '.join(u.name for u in self.participants.all())
        return f'Conversation: {names}'

    def other_user(self, me):
        return self.participants.exclude(pk=me.pk).first()

    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class DirectMessage(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.name}: {self.content[:40]}'


class ChatGroup(models.Model):
    """Group chat room."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='group_avatars/', blank=True, null=True)
    admin = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='administered_groups')
    members = models.ManyToManyField(CustomUser, related_name='chat_groups', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()

    def last_message(self):
        return self.group_messages.order_by('-created_at').first()


class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name='group_messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='group_messages_sent')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.group.name}] {self.sender.name}: {self.content[:40]}'
