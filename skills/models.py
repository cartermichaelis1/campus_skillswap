from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    PRICE_CHOICES = [
        ('free', 'Free / Volunteer'),
        ('exchange', 'Skill Exchange'),
        ('paid', 'Paid'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='skills'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='skills'
    )
    price_type = models.CharField(max_length=20, choices=PRICE_CHOICES, default='free')
    contact_info = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('skill_detail', args=[self.pk])

    def average_rating(self):
        result = self.reviews.aggregate(avg=Avg('rating'))
        if result['avg'] is not None:
            return round(result['avg'], 1)
        return None

    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('skill', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.username} → {self.skill.title} ({self.rating}★)"
