from django.urls import path

from .views import MembershipSelectView,PaymentView,updateTransactions,profile_view

app_name = 'membership'

urlpatterns = [
    path('',MembershipSelectView.as_view(),name='select'),
    path('payment/',PaymentView,name='payment'),
    path('update-transactions/<subscription_id>/',updateTransactions,name='update-transactions'),
    path('profile/',profile_view,name='profile')

]