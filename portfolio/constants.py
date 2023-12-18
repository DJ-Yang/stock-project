from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class TransactionType(TextChoices):
    DEPOSIT = ("DEPOSIT", _("DEPOSIT")) # 입금
    WITHDRAW = ("WITHDRAW", _("WITHDRAW")) # 출금
    BUY = ("BUY", _("BUY")) # 증권 구매
    SELL = ("SELL", _("SELL")) # 증권 판매


class ReqeustType(TextChoices):
    HIGH_RISK = ("HIGH_RISK", _("HIGH_RISK")) # 원화 잔고 전부 활용
    STABLE = ("STABLE", _("STABLE")) # 원화 잔고 절반만 활용


class RequestStatus(TextChoices):
    REQUEST = ("REQUEST", _("REQUEST")) # 유저가 자문을 요청함.
    AWAITING = ("AWAITING", _("AWAITING")) # 에임에서 포트폴리오를 구성하여 유저의 승인을 기다림.
    COMPLETE = ("COMPLETE", _("COMPLETE")) # 유저가 자문을 승인함.
    REJECT = ("REJECT", _("REJECT")) # 유저가 자문 계약을 거절함.
