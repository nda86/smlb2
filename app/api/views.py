# coding=utf-8
import os
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes, api_view
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from main.models import Org, Shop
from converter.worker import Worker
from api.utils import get_logger_file


logger = get_logger_file(__name__, 'smlb_debug.log')


# ******************************************АУТЕНТИФИКАЦИЯ***************************************************
# получение токена
@csrf_exempt
@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request, format=None):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            Response({'error': 'Please provide both username and password.'}, status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid Credentials'}, status.HTTP_404_NOT_FOUND)
        token, created = Token.objects.get_or_create(user=user)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response({'token': token.key}, status_code)
    except Exception as e:
        logger.exception(e)
        return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ***********************************************************************************************************


# ***************************api***********************************************************************
class Goods(APIView):
    @staticmethod
    def post(request, format='JSON'):
        try:
            sm_shop = request.data.get("sm_shop")
            # get current user
            user = request.user
            # get client_id from model Org by user
            org = Org.objects.filter(user=user).first()
            if not org:
                return Response({"error": "Client don't have any Organisation"}, status=status.HTTP_402_PAYMENT_REQUIRED)
            shop = Shop.objects.filter(org=org).filter(sm_id=sm_shop).first()
            if not shop:
                return Response({"error": "Shop {} was not found".format(sm_shop)}, status=status.HTTP_402_PAYMENT_REQUIRED)
            classif = request.data.get("classif")
            if not classif:
                classif = "1"
            lb_token = request.data.get("lb_token")

            # path это имя файла товара загруженного на серер
            # или строка xml в base64
            # path = base64.b64decode(request.data.get("goods_data"))
            path = request.data.get("goods_data")

            args_dict = {
                "owner_id": org.lb_id,
                "obj_id": shop.lb_id,
                "type": "goods",
                "lb_token": lb_token,
                "classif": classif,
                "path": path
            }

            worker = Worker(args=args_dict)
            res, status_code = worker.work()
            return Response(res, status_code)
        except Exception as e:
            logger.exception(e)
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Reports(APIView):
    @staticmethod
    def post(request, format='JSON'):
        try:
            # get parameters via headers
            beg_date = request.data.get("beg_date")
            end_date = request.data.get("end_date")
            # get lb_token
            lb_token = request.data.get("lb_token")
            #  приходят парметры вида смаркет
            sm_shop = request.data.get("sm_shop")
            # get curent user
            user = request.user
            # get client_id from model Org by user
            org = Org.objects.filter(user=user).first()
            if not org:
                return Response({"error": "Client don't have any Organisation"}, status=status.HTTP_404_NOT_FOUND)
            shop = Shop.objects.filter(org=org).filter(sm_id=sm_shop).first()
            if not shop:
                return Response({"error": "Shop {} was not found".format(sm_shop)}, status=status.HTTP_404_NOT_FOUND)
            if not status:
                return Response({"error": "Not connection to Litebox..."}, status=status.HTTP_404_NOT_FOUND)

            args_dict = {
                "client_id": org.client_id,
                "owner_id": org.lb_id,
                "obj_id": shop.lb_id,
                "beg_date": beg_date,
                "end_date": end_date,
                "type": "reports",
                "sm_shop": sm_shop,
                "lb_token": lb_token
            }

            worker = Worker(args=args_dict)
            files, status_code = worker.work()
            arr_files = []
            for file in files:
                with open(file, "r") as f:
                    file_data = f.read()
                    file_name = os.path.basename(f.name)
                    x = {"file_name": file_name, "file_data": file_data}
                    arr_files.append(x)
            res = {"data": arr_files}
            return Response(res, status_code)
        except Exception as e:
            logger.exception(e)
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Sync(APIView):
    @staticmethod
    def post(request, format='JSON'):
        try:
            lb_token = request.data.get("lb_token")
            worker = Worker(args={"type": "sync", "lb_token": lb_token})
            res, status_code = worker.work()
            return Response(res, status_code)
        except Exception as e:
            logger.exception(e)
            return Response({"status": "error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# ********************************************************************************************************************
