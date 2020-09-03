# coding=utf-8
# делает из файла выгрузки смаркет Cash.dat массив объектов для передачи по API в ЛБ

import xml.etree.ElementTree as Et
from .config import MEASUREMENT


class MakeJsonGoodsSet:
    def __init__(self):
        self.goods = {}
        self.doc_price = {}

    def _set_goods(self, path, classif, flag_file=True):
        # выцепляем строки с товаром
        # меняем path вмесо имени файла приходит строка
        if not flag_file:
            root = Et.fromstring(path)
        else:
            root = Et.parse(path)
        for goods in root.iter("good"):
            delete_from_cash = goods.find("delete-from-cash")
            if delete_from_cash is not None:
                continue
            code = goods.get("marking-of-the-good")
            name = goods.find("name").text
            ves_id = goods.find("measure-type").get("id").upper()
            ves = MEASUREMENT[ves_id]
            # ves = MEASUREMENT["ШТ"] if ves_id == "ШТ" else MEASUREMENT["КГ"]
            # product_type = goods.find("product-type").text
            # ves = MEASUREMENT["ШТ"] if product_type == "ProductPieceEntity" else MEASUREMENT["КГ"]
            sale_price = goods.find("price-entry").get("price")
            barcodes = goods.findall("bar-code")
            barcodes_arr = []
            for bar in barcodes:
                barcodes_arr.append({"barcode": bar.get("code")})

            data = {
                "code": code,
                "name": name,
                "full_name": name,
                "wareskind_code": None,
                "main_unit_id": ves,
                "wg_id": classif,
                "producer_id": None,
                "importer_id": None,
                "tax_id": 7,
                "alccode": None,
                "wares_parent":  1,
                "wares_type_code": "0",
                "wares_type_name": "Материальная ценность",
                "country_code": None,
                "country_name": None,
                "volume_value": None,
                "proof_value": None,
                "barcodes": barcodes_arr,
                "external_id": None,
                "external_code": None,
                "sale_price": sale_price
            }
            self.goods[code] = data

    def make_goods(self, path, classif, flag_file):
        self._set_goods(path, classif, flag_file=flag_file)
        return self.goods

    def make_doc_price(self, cargo, today, owner_id, obj_id):
        summa = 0
        self.doc_price = {
                "type_doc": "OVERVALUE",
                "number_doc": "x123",
                "doc_date": today,
                "real_doc_date": today,
                "from_id": obj_id,
                "to_id": None,
                "through_id": None,
                "owner_id": owner_id,
                "status": "",
                "registr_egais": None,
                "dbase": None,
                "descript": "",
                "summa": 0,
                "external_id": None,
                "username": None,
                "cargo": []
                }
        for x in cargo:
            d = {
                    "doc_sum": x["price"],
                    "price": x["price"],
                    "wares_id": x["wares_id"],
                    "egais": [
                        {
                            "informbregid": None,
                            "ttninformbregid": None,
                            "amount": None,
                            "registregais": None,
                            "informaregid": None,
                            "identity": None
                        }
                            ],
                    "self_calc": None,
                    "quantity": 1
                    }
            summa = summa + float(x["price"])
            self.doc_price["cargo"].append(d)
        self.doc_price["summa"] = summa
        return self.doc_price

