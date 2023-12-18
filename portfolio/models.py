from django.db import models
from django.utils.translation import gettext_lazy as _

from portfolio.constants import TransactionType, ReqeustType, RequestStatus


class Account(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE)
    balance = models.PositiveIntegerField(_("Balance"))


class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(_("Type"), max_length=8, choices=TransactionType.choices)
    amount = models.PositiveIntegerField(_("Amount"))
    description = models.CharField(_("Description"), max_length=64, null=True, blank=True)


class Request(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE)
    request_type = models.CharField(_("Request Type"), max_length=16, choices=ReqeustType.choices)
    status = models.CharField(_("Status"), max_length=16, choices=RequestStatus.choices, default=RequestStatus.REQUEST)


class Stock(models.Model):
    code = models.CharField(_("Code"), max_length=8, unique=True)
    name = models.CharField(_("Name"), max_length=32)
    price = models.PositiveIntegerField(_("Price"))


class StockOrder(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(_("Count"))
    price_per_share = models.PositiveIntegerField(_("Price per share"))


class StockUserList(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(_("Count"))
