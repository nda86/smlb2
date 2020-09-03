from django.contrib import admin
from .models import Wares


@admin.register(Wares)
class AdminWares(admin.ModelAdmin):
    fields = ("user", "sm_code", "lb_code", "name_hash")
    list_display = ("user", "sm_code", "lb_code", "name_hash")
