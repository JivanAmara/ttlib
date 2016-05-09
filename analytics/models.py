from __future__ import unicode_literals

from django.db import models
from tonerecorder.models import RecordedSyllable


class MaxFreq11(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq18(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq28(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq38(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq48(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq58(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq68(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq78(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreq88(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange28(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange38(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange48(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange58(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange68(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange78(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()

class PeakFreqChange88(models.Model):
    recording = models.OneToOneField(RecordedSyllable, null=True)
    attr = models.FloatField()
