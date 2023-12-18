from portfolio.models import Account

class PortfolioService:

    @staticmethod
    def create_account_per_user(user):
        return Account.objects.create(
            user=user,
            balance=0,
        )
