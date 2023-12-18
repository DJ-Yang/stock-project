from django.urls import path
from portfolio import views


urlpatterns = [
    path('', views.PortfolioAPIView.as_view()),
    path('stock/', views.StockListCreateAPIView.as_view()),
    path('stock/<int:pk>', views.StockRetrieveUpdateDestroyAPIView.as_view()),
    path('request/', views.RequestAPIView.as_view()),
    path('balance/', views.BalanceAPIView.as_view()),
]
