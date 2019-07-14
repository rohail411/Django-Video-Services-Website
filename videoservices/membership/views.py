from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import ListView
from django.conf import settings
from .models import Membership,UserMembership,Subscription
import stripe
# Create your views here.

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None

def get_selected_membership(request):
    membership_type = request.session['selected_membership_type']
    selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

def profile_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_membership(request)
    context = {
        'user_membership':user_membership,
        'user_subscription':user_subscription
    }
    return render(request,'membership/profile.html',context)

class MembershipSelectView(ListView):
    model = Membership
    template_name = 'membership_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context
    def post(self,request,**kwargs):
        selected_membership_type = request.POST.get('membership_type')

        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)

        selected_membership_qs = Membership.objects.filter(membership_type=selected_membership_type)
        if selected_membership_qs.exists():
            selected_membership = selected_membership_qs.first()

        """
        ==========
        Validation
        ==========
        """
        if user_membership.membership == selected_membership:
            if user_subscription != None:
                messages.info(request,"You already have this Membership. Your \ next payment is due".format('get the value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFFERER'))

            # Assign to the session
        request.session['selected_membership_type'] = selected_membership.membership_type

        return HttpResponseRedirect(reverse('membership:payment'))

def PaymentView(request):

    user_membership = get_user_membership(request)

    selected_membership = get_selected_membership(request)

    publishKey = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        try:
            token = request.POST['stripeToken']
            subscription = stripe.Subscription.create(
                  customer=user_membership.stripe_customer_id,
                  items=[
                    {
                      "plan": selected_membership.stripe_plan_id,
                    },
                  ],
                source = token
                )
            redirect(reverse('membership:update-transactions',kwargs={
                'subscription_id':subscription.id
            }))
        except:
            messages.info(request,"Your Card Has been Declined")
    context = {
        'publishKey':publishKey,
        'selected_membership':selected_membership
    }
    return render(request,'membership/membership_payment.html',context)

def updateTransactions(request,subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)

    user_membership.membership = selected_membership
    user_membership.save()

    sub,created = Subscription.objects.get_or_create(user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass
    messages.info(request,f'Successfully created {selected_membership} membership')
    return redirect('/courses')