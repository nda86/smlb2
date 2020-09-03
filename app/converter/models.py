# coding=utf-8
from django.db import models
from django.contrib.auth.models import User
from api.utils import get_current_user


class Wares(models.Model):
    class Meta:
        verbose_name = "Таблица кодов товара"
        unique_together = ("user", "sm_code", "lb_code")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="goods")
    sm_code = models.CharField(max_length=10, verbose_name="Код товара в Смаркет")
    lb_code = models.CharField(max_length=10, verbose_name="wares_id товара в Лайтбокс")
    name_hash = models.CharField(max_length=32, verbose_name="hash value of name and barcodes", null=True, blank=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.user = user
        super(Wares, self).save(*args, **kwargs)


def goods_clear():
    Wares.objects.all().delete()


def goods_insert(sm_code, lb_code, name_hash):
    Wares.objects.create(sm_code=sm_code, lb_code=lb_code, name_hash=name_hash)


def goods_exsist(sm_code, name_hash):
    user = get_current_user()
    # ищем товар в таблице
    ware = Wares.objects.filter(user=user, sm_code=sm_code, name_hash=name_hash).first()
    if ware is not None:
        return True, ware.lb_code
    else:
        return False, ""


def goods_get_sm_code(lb_code):
    user = get_current_user()
    ware = Wares.objects.filter(user=user, lb_code=lb_code).first()
    if ware is not None:
        return ware.sm_code
    else:
        return "00000"


def goods_update(sm_code, lb_code, name_hash):
    Wares.objects.update_or_create(lb_code=lb_code,
                                   defaults={"sm_code": sm_code, "lb_code": lb_code, "name_hash": name_hash})
