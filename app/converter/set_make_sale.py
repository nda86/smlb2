# coding=utf-8
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree, fromstring
from main.models import Cash
from .models import goods_get_sm_code
from .utils import prettify
from .config import TMP_REPORTS


class MakeSaleDocSet:
    def __init__(self, **kwargs):
            # client_id
            # sm_shop
            # beg_date
            # end_date
        self.__dict__.update(kwargs)
        self.files = []

    def _write_xml(self, et, day, session_id, sm_cash, type):
        d = day.split()[0].split("-")
        date = "{0}.{1}.{2}".format(d[2], d[1], d[0])
        filename = "{type}-{day}-{client_id}-{sm_shop}-{sm_cash}-{session_id}.xml".format(
            type=type,
            day=date,
            client_id=str(self.client_id),
            sm_shop=str(self.sm_shop),
            session_id=session_id,
            sm_cash=sm_cash)
        # create path to save xml
        _file = os.path.join(TMP_REPORTS, self.client_id, filename)
        # create dir /client_id/, if it's not then create
        os.makedirs(os.path.dirname(_file), exist_ok=True)
        et.write(_file, encoding="utf-8",  xml_declaration=True)
        return _file

    def _get_sm_cash(self, lb_id):
        cash = Cash.objects.filter(lb_id=lb_id).first()
        return getattr(cash, "sm_id", None)

    def _make_zreport(self, sale):
        z = sale["z_report"]
        sm_cash = self._get_sm_cash(z["equipment_id"])
        if not sm_cash:
            return {"error": "cash not found"}
        reports = Element("reports")
        reports.set("count", "1")
        zreport = Element("zreport")

        SubElement(zreport, "reportType").text = "ZReport"
        SubElement(zreport, "shiftNumber").text = str(z["session_id"])
        SubElement(zreport, "shopNumber").text = str(self.sm_shop)
        SubElement(zreport, "docNumber").text = str(z["doc_number"])
        SubElement(zreport, "cashNumber").text = str(sm_cash)
        SubElement(zreport, "serialCashNumber").text = "0000000000000000"
        SubElement(zreport, "userTabNumber").text = str(z["user_id"])
        SubElement(zreport, "userName").text = "Kassir {}".format(str(z["user_id"]))
        SubElement(zreport, "dateOperDay").text = str(z["date_beg"])
        SubElement(zreport, "dateShiftClose").text = str(z["date_end"])
        SubElement(zreport, "dateShiftOpen").text = str(z["date_beg"])
        SubElement(zreport, "countCashPurchase").text = str(z["cnt_salecash"])
        SubElement(zreport, "countCashlessPurchase").text = str(z["cnt_salenoncash"])
        SubElement(zreport, "countReturn").text = str(z["cnt_ret"])
        SubElement(zreport, "counterIncoming").text = "0"
        SubElement(zreport, "counterWithdrawal").text = "0"
        SubElement(zreport, "amountByCashPurchase").text = str(z["amount_salecash"])
        SubElement(zreport, "amountByCashlessPurchase").text = str(z["amount_salenoncash"])
        SubElement(zreport, "amountByReturnFiscal").text = str(z["amount_retcash"])
        SubElement(zreport, "amountCashIn").text = str(z["amount_cashin"])
        SubElement(zreport, "amountCashOut").text = str(z["amount_cashout"])
        SubElement(zreport, "amountCashDiscount").text = "0"
        SubElement(zreport, "returnDiscountCashPay").text = "0"
        SubElement(zreport, "incresentTotalStart").text = "0"
        SubElement(zreport, "incresentTotalFinish").text = "0"
        SubElement(zreport, "incresentTotalReturnStart").text = "0"
        SubElement(zreport, "incresentTotalReturnFinish").text = "0"
        SubElement(zreport, "factoryCashNumber").text = "0000000000"
        SubElement(zreport, "cashName").text = str(z["equipment_name"])
        SubElement(zreport, "inn").text = "0000000000"
        payments = SubElement(zreport, "payments")

        a = SubElement(payments, "payment")
        a.set("typeClass","CashPaymentEntity")
        a.set("amountPurchase", str(z["amount_salecash"]))

        b = SubElement(payments, "payment")
        b.set("typeClass","BankCardPaymentEntity")
        b.set("amountPurchase", str(z["amount_salenoncash"]))

        reports.append(zreport)
        root = fromstring(prettify(reports))
        et = ElementTree(root)
        filename = self._write_xml(et=et, type="zreports", sm_cash=sm_cash, session_id=z["session_id"], day=z["date_end"])
        self.files.append(filename)

    def _make_purchases(self, sale):
        z = sale["z_report"]
        sm_cash = self._get_sm_cash(z["equipment_id"])
        if not sm_cash:
            return {"error": "cash not found"}
        purchases = Element("purchases")
        checks = sale["documents"]
        purchases.set("count", str(len(checks)))
        for check in checks:
            # определяем тип операции, возврат или нет
            operation_type = True if str(check["type_doc"]) == "SALE" else False
            cargo_cnt = 0
            purchase = Element("purchase")

            purchase.set("tabNumber", str(z["user_id"]))
            purchase.set("userName", "Kassir")
            purchase.set("operationType", str(operation_type))
            purchase.set("operDay", str(z["date_beg"]))
            purchase.set("shop", str(self.sm_shop))
            purchase.set("cash", str(sm_cash))
            purchase.set("shift", str(z["session_id"]))
            purchase.set("number", str(int(check["doc_id"])))
            purchase.set("saletime", str(check["doc_date"]))
            purchase.set("begintime", str(check["doc_date"]))
            purchase.set("amount", str(check["summa"]))
            purchase.set("discountAmount", "0")
            purchase.set("inn", "0000000000")

            positions = SubElement(purchase, "positions")

            for cargo in check["cargo"]:
                cargo_cnt = cargo_cnt + 1
                goods_code = self._get_code_by_wares_id(cargo["wares_id"])
                position = Element("position")
                position.set("order", str(cargo_cnt))
                position.set("departNumber", "1")
                position.set("goodsCode", str(goods_code))
                position.set("barCode", "")
                position.set("count", str(cargo["quantity"]))
                position.set("cost", str(cargo["price"]))
                position.set("nds", "0")
                position.set("ndsSum", "0")
                position.set("discountValue", "0")
                position.set("costWithDiscount", str(cargo["price"]))
                position.set("amount", str(cargo["doc_sum"]))
                position.set("dateCommit", str(check["doc_date"]))
                positions.append(position)

            doc_payments = check["doc_payment"][0]
            payments = Element("payments")
            if str(doc_payments["pay_type_code"]) in ("CASHSALE", "CASHRET"):
                a = SubElement(payments, "payment")
                a.set("typeClass", "CashPaymentEntity")
                a.set("amount", str(doc_payments["summ_get"]))
                a.set("description", "CASHSALE")

                b = SubElement(payments, "payment")
                b.set("typeClass", "CashChangePaymentEntity")
                b.set("amount", str(doc_payments["summ_rest"]))
                b.set("description", "")
            else:
                a = SubElement(payments, "payment")
                a.set("typeClass", "BankCardPaymentEntity")
                a.set("amount", str(doc_payments["summ_get"]))
                a.set("description", "NONCASHSALE")
            purchase.append(payments)
            purchases.append(purchase)
        root = fromstring(prettify(purchases))
        et = ElementTree(root)
        filename = self._write_xml(et=et, type="purchases", sm_cash=sm_cash, session_id=z["session_id"], day=z["date_end"])
        self.files.append(filename)

    def _get_code_by_wares_id(self, wares_id):
        return goods_get_sm_code(wares_id)

    def make_doc(self, sale):
        self._make_zreport(sale)
        self._make_purchases(sale)
