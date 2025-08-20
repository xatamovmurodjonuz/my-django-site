from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    image = models.ImageField(upload_to='business_images/', null=True, blank=True)
    is_premium = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='businesses')

    def __str__(self):
        return self.name

    def total_likes(self):
        # Likes with value=1
        return self.likes.filter(value=1).count()

    def total_dislikes(self):
        # Likes with value=-1
        return self.likes.filter(value=-1).count()

class Comment(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.author.username} on {self.business.name}'

class Rating(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('business', 'user')
        ordering = ['-stars']  # ixtiyoriy, reytinglarni yulduzlar bo'yicha tartiblaydi

    def __str__(self):
        return f'{self.stars} stars by {self.user.username} for {self.business.name}'

class Like(models.Model):
    LIKE_CHOICES = (
        (1, 'Like'),
        (-1, 'Dislike'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='likes')
    value = models.SmallIntegerField(choices=LIKE_CHOICES)

    class Meta:
        unique_together = ('user', 'business')

    def __str__(self):
        return f"{self.get_value_display()} by {self.user.username} for {self.business.name}"
