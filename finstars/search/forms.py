from django import forms


class PlanetSearchForm(forms.Form):
    PLANETS = [
        ('Sa', 'Saturn'),
        ('Gu', 'Jupiter'),
        ('Ma', 'Mars'),
        ('Sk', 'Venus'),
        ('Bu', 'Mercury'),
        ('Su', 'Sun'),
        ('Ch', 'Moon'),
        ('Ra', 'Mean Node'),
    ]

    ZODIAC_SIGNS = [(str(i), f'{i}') for i in range(1, 13)]

    planet = forms.ChoiceField(choices=PLANETS, required=True)
    zodiac_sign = forms.ChoiceField(choices=ZODIAC_SIGNS, required=True)
    retrograde = forms.BooleanField(required=False, label="Ретроградность")

