# coding=utf-8
from django.contrib import admin
from main.models import *


class CashesInLine(admin.TabularInline):
    model = Cash
    extra = 0
    fields = ("name", "sm_id", "lb_id",)


@admin.register(Org)
class AdminOrg(admin.ModelAdmin):
    fields = ("name", "client_id", "lb_id", "user")
    list_display = ("name", "client_id",)

    def has_add_permission(self, request):
        return False if Org.objects.count() > 0 else super().has_add_permission(request)

    def save_model(self, request, obj, form, change):
        user = request.user
        obj = form.save(commit=True)
        if not change or not obj.user:
            obj.user = user
        obj.save()
        form.save_m2m()
        return obj


@admin.register(Shop)
class AdminShop(admin.ModelAdmin):
    exclude = ("user",)
    fields = ('org', 'name', 'sm_id', 'lb_id',)
    list_display = ('name',)
    inlines = (CashesInLine,)
