from django.contrib import admin

from portfolio.models import Stock, Request, Transaction, Account, StockUserList, StockOrder


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    pass


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    pass


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    pass


@admin.register(StockOrder)
class StockOrder(admin.ModelAdmin):
    pass


@admin.register(StockUserList)
class StockUserListAdmin(admin.ModelAdmin):
    pass