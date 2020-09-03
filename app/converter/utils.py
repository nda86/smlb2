import hashlib
import requests
from xml.etree import ElementTree
from xml.dom import minidom
from .models import goods_insert
from .config import API_URLS


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


# генерируем хеш товара
def make_goods_hash(g):
    value = "{name}-{barcodes}".format(name=g["name"], barcodes=",".join(str(x) for x in g["barcodes"]))
    return hashlib.md5(value.encode("utf-8")).hexdigest()


# класс для передачи http запросов на сервер ЛБ
class Connect:
    def __init__(self, token):
        self.headers = {}
        self.token = token

    # check auth for LB via token
    def auth(self):
        self.headers = {
            'Authorization': 'Token ' + self.token
        }
        # test connection for LB
        url = "{}?page=1&limit=1".format(API_URLS["GOODS"])
        status_code = self.get(url).status_code
        if status_code != 200:
            return False, self.token
        else:
            return True, self.token

    # делаем пост запрос
    def post(self, api_url, data):
        r = requests.post(api_url, headers=self.headers, json=data)
        return r

    # делаем пост запрос
    def put(self, api_url, wares_id, data):
        r = requests.put(api_url + "/" + str(wares_id) + "/saleprice", headers=self.headers, json=data)
        return r

    # делаем пост запрос
    def get(self, api_url):
        r = requests.get(api_url, headers=self.headers)
        return r


# класс для выполнения синхронизации товаров в базе лб и смаркет
class Synchroniser:
    def __init__(self, connect):
        self.connect = connect
        self.count_goods = 0

    def _parse(self, url):
        for x in range(99):
            r = self.connect.get(url + '?page=' + str(x))
            if r.status_code == 500:
                return
            data = r.json()['data']
            self.count_goods = self.count_goods + len(data)
            for g in data:
                code = g['code']
                wares_id = g['wares_id']
                name_hash = make_goods_hash(g)
                goods_insert(code, wares_id, name_hash)

    def sync_goods(self, url):
        self._parse(url)


