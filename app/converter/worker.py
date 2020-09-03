# coding=utf-8
from datetime import date
from random import Random
from rest_framework import status
from .utils import Connect, Synchroniser
from converter import set_make_goods, set_make_sale
from .config import API_URLS
from .models import goods_clear, goods_update, goods_exsist
from api.utils import get_logger_file
from .utils import make_goods_hash


class Worker:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs["args"])
        self.logger = get_logger_file(__name__, "{file}-{obj_id}-{random}.log".format(file=__name__.lower(),
                                    obj_id=getattr(self, "obj_id", ""), random=Random().randrange(1, 1000)))
            # "client_id"
            # "owner_id"
            # "obj_id"
            # "beg_date"
            # "end_date"
            # "type"
            # "sm_shop"
            # "lb_token"
            # "classif"
            # "path"
        self.today = date.today().strftime("%d.%m.%Y")
        self.cargo = []
        self.count = 0
        self.maker_sale = None
        self.maker_goods = None
        self.sync_goods = None
        # соединяемся с сервером ЛБ
        self.connect = Connect(self.lb_token)

    def do_sync_all(self):
        goods_clear()
        self.logger.debug("Start SYNCING")
        self.sync_goods.sync_goods(API_URLS["GOODS"])
        self.logger.debug("End SYNCING")

    def do_load_goods(self, path, classif, flag_file):
        goods = self.maker_goods.make_goods(path=path, classif=classif, flag_file=flag_file)
        self.logger.debug("Count of goods to load is {}.".format(len(goods.values())))
        for g in goods.values():
            # выдираем цену из json
            sale_price = g.pop("sale_price", None)
            # запоминаем код товара СМ
            sm_code = g["code"]
            # вычисляем hash, если поменяется хоть буква в имени или штрихкод, то объект следует перевыгрузить в ЛБ
            name_hash = make_goods_hash(g)
            # если товар с кодом и hash есть, значит он уже загружен и не менялся, и повторное его не выгружаем
            exsist, lb_code = goods_exsist(sm_code, name_hash)
            if exsist:
                self.logger.debug("Goods with sm_code {} not changed".format(sm_code))
                wares_id = lb_code
                self.cargo.append({"wares_id": wares_id, "price": sale_price})
                self.count += 1
                if self.count > 999: self.do_load_price()
            else:
                # отправляем товар в ЛБ
                r = self.connect.post(API_URLS["GOODS"], g)
                self.logger.debug("add goods with sm_code {}: {}".format(sm_code, r.json()))
                self.count += 1
                if r.status_code not in (200,201):
                    self.logger.error("Response: {}, count: {}".format(r.json(), self.count))
                    continue
                else:
                    # получаем в ответ wares_id и добавляем его в DB
                    data = r.json()
                    wares_id = data["wares_id"]
                    goods_update(sm_code, wares_id, name_hash)
                    #  запоминаем цену товара для создания дока установки цен
                    self.cargo.append({"wares_id": wares_id, "price": sale_price})
                    if self.count > 999: self.do_load_price()

    def do_load_price(self):
        doc_price = self.maker_goods.make_doc_price(self.cargo, self.today, self.owner_id, self.obj_id)
        self.logger.debug("cargo: {}, today: {}, owner_id: {}, obj_id: {}".format(self.cargo, self.today,
                                                                                  self.owner_id, self.obj_id))
        r = self.connect.post(API_URLS["DOC"], doc_price)
        self.logger.debug("add doc_price: {}".format(r.json()))
        self.count = 0
        self.cargo = []

    def do_make_sale(self):
        url = "{0}?date_beg={1}&date_end={2}&org_id={3}&shop_id={4}".format(API_URLS["SESSION"],
                                         self.beg_date, self.end_date, self.owner_id, self.obj_id)
        r = self.connect.get(url)
        sessions = r.json().get("data", [])
        for session in sessions:
            url = "{0}/{1}".format(API_URLS["SESSION"], session["session_id"])
            r = self.connect.get(url)
            self.maker_sale.make_doc(r.json()["data"][0])

    def work(self):
        connection_status, token = self.connect.auth()
        if not connection_status:
            return {"status": "error", "msg": "Not connection to Litebox..."}, status.HTTP_401_UNAUTHORIZED
        if self.type == "reports":
            # создаем объект для создания з отчета в СМ в этом случае в kwargs при создании worker
            # надо передать все параметры ниже
            self.maker_sale = set_make_sale.MakeSaleDocSet(
                client_id=self.client_id,
                sm_shop=self.sm_shop,
                beg_date=self.beg_date,
                end_date=self.end_date)
            self.do_make_sale()
            files = self.maker_sale.files
            # zip_file = self._create_zip(files)
            return files, status.HTTP_200_OK
        elif self.type == "sync":
            # создаем объект для синхронизации кодов
            self.sync_goods = Synchroniser(self.connect)
            self.do_sync_all()
            return {"status": "success"}, status.HTTP_200_OK
        elif self.type == "goods":
            self.logger.debug("START")
            self.maker_goods = set_make_goods.MakeJsonGoodsSet()
            self.do_load_goods(path=self.path, classif=self.classif, flag_file=False)
            self.do_load_price()
            self.logger.debug("END")
            return {"status": "success"}, status.HTTP_200_OK
        else:
            pass
