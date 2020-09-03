# делает из файла выгрузки смаркет Cash.dat массив объектов для передачи по API в ЛБ
from datetime import datetime


class MakeJsonGoodsAtol:
	def __init__(self, path, classif):
		self.goods = {}
		self.path = path
		self.classif = classif
		self.doc_price = {}

	def _parse(self):
		# выцепляем строки с товаром
		flag_goods = 0
		flag_barcodes = 0
		with open(self.path) as goods_file:
			for x in goods_file:
				if x.strip('\n') == '$$$REPLACEQUANTITY': 
					flag_goods = flag_goods + 1
					continue
				if flag_goods == 2:
					if x[0] == "$": 
						break
					else:
						self._set_goods(x)
		with open(self.path) as goods_file:
			for x in goods_file:
				if x.strip('\n') == '$$$ADDBARCODES':
					flag_barcodes = flag_barcodes + 1
					continue
				if flag_barcodes == 1:
					if x[0] == "$":
						break
					else:
						self._set_barcodes(x)

	def _set_goods(self, x):
		# выбираем 0,2,3,4
		# 0 - код
		# 2 - наименование
		# 3 - полное наименование
		# 4 - цена
		# 7,0 - призна весового (1- вес)

		# 55 - шт
		# 15 - кг
		items = x.split(';')
		code = str(items[0]).strip()[:11]
		name = str(items[2]).strip()[:81]
		fullname = str(items[3]).strip()
		ves_flag = str(items[7]).split(',')[0]
		if ves_flag == '1':
			ves = 15
		else:
			ves = 55
		sale_price = float(items[4])
		data = {
			"code": code,
			"name": name,
			"full_name": fullname,
			"wareskind_code": None,
			"main_unit_id": ves,
			"wg_id": self.classif,
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
			"barcodes": [],
			"external_id": None,
			"external_code": None,
			"sale_price": sale_price
			}
		self.goods[code] = data

	def _set_barcodes(self, x):
		# 0 - штрихкод
		# 1 - код товара
		items = x.split(';')
		code = str(items[1]).strip()
		barcode = str(items[0]).strip()[:26]
		data = {'barcode': barcode}
		self.goods[code]["barcodes"].append(data)

	def make_goods(self):
		self._parse()
		print("{0} - {1} goods sending to load...".format(str(datetime.now()), str(len(self.goods.values()))))
		return self.goods

	def make_doc_price(self, cargo, today, obj_id, owner_id):
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
			summa = summa + x["price"]
			self.doc_price["cargo"].append(d)
		self.doc_price["summa"] = summa
		return self.doc_price

