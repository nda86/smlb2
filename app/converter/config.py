# coding=utf-8
import os
from smlb.settings import BASE_DIR

# основные конфигурационные переменные и значения
# api точки
API_BASE = "https://lbe.litebox.ru/api/v1"

API_URLS = {
    "AUTH": f"{API_BASE}/auth-token",
    "GOODS": f"{API_BASE}/gwares",
    "DOC": f"{API_BASE}/document",
    "SESSION": f"{API_BASE}/session",
    }

#  коды единиц измерения
MEASUREMENT = {
    "ШТ": 55,
    "КГ": 15,
    "ЛИТР": 22
}

TMP_REPORTS = os.path.join(BASE_DIR, "tmp_xml")


def get_path():
    cd = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(cd, "catalog-goods_02.xml")
    return path
