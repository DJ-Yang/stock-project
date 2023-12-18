import logging

from django.db import transaction

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError

from portfolio.models import Transaction, Stock, StockUserList, Request, StockOrder
from portfolio.serializers import (
	StockListCreateSerializer,
	StockUpdateDestroySerializer,
	RequestSerializer,
)
from portfolio.constants import ReqeustType, RequestStatus

logger = logging.getLogger(__name__)


BALANCE_CACULATION_TYPE = {
  'DEPOSIT': 'plus',
  'WITHDRAW': 'minus',
  'BUY': 'minus',
  'SELL': 'plus',
}


def update_balance(account, amount, request_type, description=None):
	request_type_operator = BALANCE_CACULATION_TYPE.get(request_type)
	
	if request_type_operator == None:
		raise ParseError

	if request_type_operator == 'minus' and account.balance < amount:
		raise ValidationError("insufficient balance")

	Transaction.objects.create(
		account=account,
		transaction_type=request_type,
		amount=amount,
		description=description,
	)

	update_balance = account.balance + amount if request_type_operator == 'plus' else  account.balance - amount
	account.balance = update_balance
	account.save()

	logger.info("Balance Update Complete", extra={
		"account_id": account.id,
		"change_amount": amount,
		"operator": request_type_operator,
	})


class BalanceAPIView(APIView):

	def get(self, request, *args, **kwargs):
		user = request.user
		account = user.account

		return Response({'balance': account.balance}, status=status.HTTP_200_OK)

	def post(self, request, *args, **kwargs):
		user = request.user
		balance_type = request.data.get('type')
		amount = request.data.get('amount')

		if not balance_type or not amount:
			return Response({"message": 'required data missing'}, status=status.HTTP_400_BAD_REQUEST)

		with transaction.atomic():
			try:
				update_balance(account=user.account, amount=amount, request_type=balance_type)
				return Response(status=status.HTTP_200_OK)

			except ValidationError as e:
				logger.info("Failed Change Balance", extra={
					"error_msg": str(e),
					"user_id": user.id,
					"amount": amount,
				})
				return Response({"message": 'Failed Change Balance'}, status=status.HTTP_400_BAD_REQUEST)
			except ParseError as e:
				logger.info("Failed Change Balance", extra={
					"error_msg": str(e),
					"user_id": user.id,
					"type": balance_type,
				})
				return Response({"message": 'Failed Change Balance'}, status=status.HTTP_400_BAD_REQUEST)


class StockListCreateAPIView(generics.ListCreateAPIView):
	queryset = Stock.objects.all()
	serializer_class = StockListCreateSerializer


class StockRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Stock.objects.all()
	serializer_class = StockUpdateDestroySerializer



class PortfolioAPIView(APIView):
	# 포트폴리오
	def get(self, request, *args, **kwargs):
		user = request.user
		user_stock_list = user.stockuserlist_set.all()
		balance = user.account.balance
		return Response(
			{
				"owned_stock": [
					{
						"code": user_stock.stock.code,
						"name": user_stock.stock.name,
						"count": user_stock.count,
						"current_price": user_stock.stock.price 
					}
					for user_stock in user_stock_list
				],
				"balance": balance,
			}, status=status.HTTP_200_OK,
		)


	def post(self, request, *args, **kwargs):
		user = request.user
		stock_data = request.data.get('stock_data', {})
		request_id = request.data.get('request_id')
		account = user.account
		sum_price = 0

		if not stock_data:
			return Response({"message": 'Stock Data is not exist.'}, status=status.HTTP_400_BAD_REQUEST)

		stock_object_list = Stock.objects.filter(code__in=stock_data.keys())
		request = Request.objects.get(id=request_id)

		if not stock_object_list.count() == len(stock_data.keys()):
			return Response({"message": 'Invalid Stock data'}, status=status.HTTP_400_BAD_REQUEST)

		with transaction.atomic():
			for code, count in stock_data.items():
				stock = stock_object_list.get(code=code)

				StockOrder.objects.create(
					request=request,
					stock=stock,
					count=count,
					price_per_share=stock.price,
				)
				sum_price += stock.price * count

			compare_amount = account.balance if request.request_type == ReqeustType.HIGH_RISK else account.balance // 2

			if sum_price > compare_amount:
				logger.info("Failed Request Approval", extra={
					"user_id": user.id,
					"stock_data": stock_data,
					"request_id": request_id,
					"compare_amount": compare_amount,
					"sum_price": sum_price,
				})
				return Response({"message": 'insufficient balance.'}, status=status.HTTP_400_BAD_REQUEST)

			request.status = RequestStatus.AWAITING
			request.save()
		
		return Response(status=status.HTTP_200_OK)


class RequestAPIView(APIView):
	# 자문 목록 확인
	def get(self, request, *args, **kwargs):
		
		requests = Request.objects.all()

		if not request.user.is_superuser:
			requests = requests.filter(user=request.user)

		serializer = RequestSerializer(requests, many=True)

		return Response(serializer.data, status=status.HTTP_200_OK)

	# 자문 요청
	def post(self, request, *args, **kwargs):
		request_type = request.data.get('request_type')

		if request_type not in [type[0] for type in ReqeustType.choices]:
			return Response({"message": 'Invalid Request Type.'}, status=status.HTTP_400_BAD_REQUEST)

		Request.objects.create(
			user=request.user,
    		request_type=request_type,
		)
		return Response(status=status.HTTP_201_CREATED)

	# 자문 승인 및 거절
	def put(self, request, *args, **kwargs):
		# 승인 여부 확인
		user = request.user
		request_id = request.data.get('request_id')
		approval_type = request.data.get('approval_type')
		
		try:
			request_obj = Request.objects.get(id=request_id)

			if not request.status == RequestStatus.AWAITING:
				logger.info(
					"The process failed because an object in the request state was accessed.", 
					extra={
						"user_id": user.id,
						"request_id": request_id,
						"approval_type": approval_type,
					}
				)
				return Response(
					{"message": 'This is not an request pending approval.'},
					status=status.HTTP_400_BAD_REQUEST,
				)

			if not approval_type in ['APPROVE', 'REJECT']:
				return Response(
					{"message": 'Invalid approval type.'},
					status=status.HTTP_400_BAD_REQUEST,
				)

			if approval_type == 'REJECT':
				request_obj.status = RequestStatus.REJECT
				request_obj.save

				logger.info("Approval rejection has been successfully processed.", extra={
					"user_id": user.id,
					"request_id": request_id,
				})
				return Response(status=status.HTTP_200_OK)

			stock_order_list = request_obj.stockorder_set.all()
			sum_price = 0

			with transaction.atomic():
				for stock_order in stock_order_list:
					
					stock, created = StockUserList.objects.get_or_create(
						user=user,
						stock=stock_order.stock,
						defaults={'count':stock_order.count}
					)

					if not created:
						stock.count += stock_order.count
						stock.save()

					sum_price += stock_order.price_per_share * stock_order.count
			
				update_balance(account=user.account, amount=sum_price, request_type='BUY', description='증권 구매')
				request_obj.status = RequestStatus.COMPLETE
				request_obj.save()
			
			return Response(status=status.HTTP_200_OK)
		except Request.DoesNotExist:
			logger.info(
					"The process failed because an object does not exist", 
					extra={
						"user_id": user.id,
						"request_id": request_id,
						"approval_type": approval_type,
					}
				)
			return Response({"message": 'Request is does not exist.'}, status=status.HTTP_400_BAD_REQUEST,)







