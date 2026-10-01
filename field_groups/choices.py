"""Choices for the example model."""

from nautobot.apps.choices import ChoiceSet


class VehicleKindChoices(ChoiceSet):
    """What kind of vehicle an example record describes; picks which of its columns apply."""

    CAR = "car"
    VAN = "van"
    MOTORBIKE = "motorbike"
    BICYCLE = "bicycle"

    CHOICES = (
        (CAR, "Car"),
        (VAN, "Van"),
        (MOTORBIKE, "Motorbike"),
        (BICYCLE, "Bicycle"),
    )


class FuelChoices(ChoiceSet):
    """How a motorised vehicle is powered."""

    PETROL = "petrol"
    DIESEL = "diesel"
    ELECTRIC = "electric"

    CHOICES = (
        (PETROL, "Petrol"),
        (DIESEL, "Diesel"),
        (ELECTRIC, "Electric"),
    )
