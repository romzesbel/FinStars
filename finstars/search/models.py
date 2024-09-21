from django.db import models


class PlanetaryPosition(models.Model):
    planet = models.CharField(max_length=2)  # Например, 'Sk', 'Bu'
    zodiac_sign = models.CharField(max_length=2)  # Например, '1' для Овна
    retrograde = models.BooleanField(default=False)  # Ретроградный ли период
    date = models.DateField()  # Дата, на которую зафиксированы данные

    def __str__(self):
        return f"{self.planet} in {self.zodiac_sign} on {self.date}"
