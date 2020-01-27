from django.db import models


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        """Return singleton and creates it if needed"""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SmtpSettings(SingletonModel):

    user = models.CharField(max_length=255, default="")
    password = models.CharField(max_length=255, default="")
    host = models.CharField(max_length=255, default="")
    port = models.CharField(max_length=255, default="")
    addr_from = models.CharField(max_length=255, default="")
    addr_to = models.CharField(max_length=255, default="")
