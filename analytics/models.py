from __future__ import unicode_literals

from django.db import models
from tonerecorder.models import RecordedSyllable


class MinFreq11(models.Model):
    recording = models.ForeignKey(RecordedSyllable, null=True)
    attr = models.FloatField()

class MaxFreq11(models.Model):
    recording = models.ForeignKey(RecordedSyllable, null=True)
    attr = models.FloatField()
