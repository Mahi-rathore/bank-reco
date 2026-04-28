from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    min_income = models.IntegerField()
    risk_level = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return self.name