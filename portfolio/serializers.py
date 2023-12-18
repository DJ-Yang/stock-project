from rest_framework import serializers

from portfolio.models import Stock, Request


class StockListCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('id', 'code', 'name', 'price')
        read_only_field = 'id'


class StockUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('price',)


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

