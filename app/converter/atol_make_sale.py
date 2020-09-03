class MakeSaleDocAtol:
	def __init__(self, sql):
		self.sql = sql
		self.transactions = {
			"62": "{number_tr};{date_tr};{time_tr};62;{code_rm};{number_doc};{code_kassir};;0;0;0;0;{session_id};0;0;0;;0;0;0;0;0;0;0;0",
			"61": "{number_tr};{date_tr};{time_tr};61;{code_rm};{number_doc};{code_kassir};;{total};0;{total};0;{session_id};0;0;0;;0;0;0;0;0;0;0;0",
			"42": "{number_tr};{date_tr};{time_tr};42;{code_rm};{number_doc};{code_kassir};;;0;0;0;0;{session_id};0;0;0;;;{total_purchase};0;0;0;0;0;;0;0;0;;",
			"11": "{number_tr};{date_tr};{time_tr};11;{code_rm};{number_doc};{code_kassir};{goods_code};;{goods_price};{goods_quantity};{goods_summa};0;{session_id};{goods_summa};{goods_summa};0;;;{goods_summa}",
			"55": "{number_tr};{date_tr};{time_tr};55;{code_rm};{number_doc};{code_kassir};;;0;{total_count};{total_purchase};0;{session_id};0;0;0;;;{total_purchase};",
		}

		self.number_tr = 0
		self.code_rm = 1
		self.code_kassir = 1
		self.session_id = 0
		pass

	@staticmethod
	def _make_date_time(date_time):
		# 2018-11-22 10:46:04.00 => ("22-11-2018", "10:46:04")
		date_arr = date_time.split(" ")[0].split("-")
		date = "{0}-{1}-{2}".format(date_arr[2], date_arr[1], date_arr[0])
		time_arr = date_time.split(" ")[1].split(":")
		time = "{0}:{1}:{2}".format(time_arr[0], time_arr[1], time_arr[2][:2])
		return date, time

	def _getnumber_tr(self):
		self.number_tr = self.number_tr + 1
		return self.number_tr

	def _open_cash(self, z):
		self.session_id = z["session_id"]
		param = {
			"date_tr": self._make_date_time(z["date_beg"])[0],
			"time_tr": self._make_date_time(z["date_beg"])[1],
			"number_tr": self._getnumber_tr(),
			"number_doc": z["doc_number"],
			"code_rm": self.code_rm,
			"code_kassir": self.code_kassir,
			"session_id": self.session_id
		}
		s = self.transactions["62"].format(**param)
		print(s)

	def _close_cash(self, z):
		param = {
			"date_tr": self._make_date_time(z["date_end"])[0],
			"time_tr": self._make_date_time(z["date_end"])[1],
			"number_tr": self._getnumber_tr(),
			"number_doc": z["doc_number"],
			"code_rm": self.code_rm,
			"code_kassir": self.code_kassir,
			"session_id": self.session_id,
			"total": z["amount_sale"],
		}
		s = self.transactions["61"].format(**param)
		print(s)

	def _add_check(self, check):
		# открываем чек
		param = {
			"date_tr": self._make_date_time(check["doc_date"])[0],
			"time_tr": self._make_date_time(check["doc_date"])[1],
			"number_tr": self._getnumber_tr(),
			"number_doc": check["number_doc"],
			"code_rm": self.code_rm,
			"code_kassir": self.code_kassir,
			"session_id": self.session_id,
			"total_purchase": check["summa"]
		}
		s = self.transactions["42"].format(**param)
		print(s)

		# добавляем позиции в чек
		for item in check["cargo"]:
			goods_code = self._get_code_by_wares_id(item["wares_id"])
			param = {
				"date_tr": self._make_date_time(check["doc_date"])[0],
				"time_tr": self._make_date_time(check["doc_date"])[1],
				"number_tr": self._getnumber_tr(),
				"number_doc": check["number_doc"],
				"code_rm": self.code_rm,
				"code_kassir": self.code_kassir,
				"session_id": self.session_id,
				"goods_summa": item["doc_sum"],
				"goods_price": item["price"],
				"goods_quantity": item["quantity"],
				"goods_code": str(goods_code)
			}
			s = self.transactions["11"].format(**param)
			print(s)

		# закрываем чек
		param = {
			"date_tr": self._make_date_time(check["doc_date"])[0],
			"time_tr": self._make_date_time(check["doc_date"])[1],
			"number_tr": self._getnumber_tr(),
			"number_doc": check["number_doc"],
			"code_rm": self.code_rm,
			"code_kassir": self.code_kassir,
			"session_id": self.session_id,
			"total_purchase": check["summa"]
		}
		s = self.transactions["55"].format(**param)
		print(s)

	def _get_code_by_wares_id(self, wares_id):
		return self.sql.get_code_by_wares_id(wares_id)

	def make_doc(self, sale):

		# ТРАНЗАКЦИИ*****************
		# 61 - открытие смены
		# 62 - открытие смены
		# 63 - отчет с гашением
 
		# 42 - открытие документа
		# 11 - регистрация товара
		# 40 - оплата с вводом суммы
		# 43 - распределение по ГП
		# 49 - закрытие документа по ГП
		# 45 - закрытие документа в ККМ
		# 55 - закрытие документа
		# ***********************************

		# # 1 - номер транзакции
		# number_tr = 0
		# # 2 - дата транзакции
		# date_tr = ''
		# # 3 - время транзакции
		# time_tr = ''
		# # 4 - код транзакции
		# code_tr = ''
		# # 5 - код рабочего места
		# code_rm = ''
		# # 6 - номер документа
		# number_doc = ''
		# # 7 - код кассира
		# code_kassir = ''
		# # 8  -str идентификатор товара
		# goods_code = ''

		with open("sale.dat", "w") as sale_file:
			# print(sale)
			z = sale["z_report"]
			# открываем смену
			self._open_cash(z)
			# получем чеки
			purchases = sale["documents"]
			# добавляем чеки
			for x in purchases:
				self._add_check(x)
			# закрываем смену
			self._close_cash(z)