from django.db import models
from django.contrib.auth.models import User


class CommonField(models.Model):
    class Meta:
        abstract = True
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="%(class)s", null=True, blank=True)
    name = models.CharField(verbose_name="Название", max_length=50)
    sm_id = models.CharField(verbose_name="Номер в Смаркет", max_length=10)
    lb_id = models.CharField(verbose_name="Номер в Лайтбоксе", max_length=10)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


    # находим текущего юзера и кладем его в объект, ПО ТОКЕНУ!!!
    # юзера находим через спец мидлверу
    # def save(self, *args, **kwargs):
    #     # меотд из utils.py
    #     user = get_current_user()
    #     if not user:
    #         user = Token.objects.get(key='')
    #     if user and user.is_authenticated:
    #         self.modified_by = user
    #         if not self.id:
    #             self.created_by = user
    #     super(CommonField, self).save(*args, **kwargs)


class Org(CommonField):
    class Meta:
        verbose_name = "Организация"
        verbose_name_plural = "Организации"
    client_id = models.CharField(verbose_name="ID клиента в Лайтбокс", max_length=10)
    sm_id = None


class Shop(CommonField):
    class Meta:
        verbose_name = "Магазин"
        verbose_name_plural = "Магазины"
    org = models.ForeignKey(Org, on_delete=models.PROTECT, related_name="shops")
    user = None


class Cash(CommonField):
    class Meta:
        verbose_name = "Касса"
        verbose_name_plural = "Кассы"
    shop = models.ForeignKey(Shop, on_delete=models.PROTECT, related_name="cashes")
    user = None
