from django.db import models

class Measurement(models.Model):
    power = models.FloatField(help_text="Puissance instantanée en watts (W)")
    voltage = models.FloatField(help_text="Tension en volts (V)")
    current = models.FloatField(help_text="Courant en ampères (A)")
    energy = models.FloatField(help_text="Énergie consommée en watt-heures (Wh)")
    timestamp = models.DateTimeField(help_text="Horodatage ISO 8601")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp} | {self.power}W {self.voltage}V {self.current}A"
