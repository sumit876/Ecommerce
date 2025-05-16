from django.shortcuts import render,redirect
from django.views import View
from django.http import JsonResponse
from .models import Customer , Cart , Payment ,OrderPlaced , Product, Wishlist
from django.db.models import Q 
from . forms import CustomerRegistrationForm ,CustomerProfileForm
from django.contrib import messages
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


# Create your views here.
@login_required
def home(request):
    totalitem=0
    wishitem = 0 
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/home.html',locals())

@login_required
def about(request):
    totalitem=0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/about.html',locals())

@login_required
def contact(request):
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/contact.html',locals())


@method_decorator(login_required,name='dispatch')
class CategoryView(View):
    def get(self,request,val):
        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request,"app/category.html",locals())
    

@method_decorator(login_required,name='dispatch')
class CategoryTitle(View):
    def get(self,request,val):
        product = Product.objects.filter(title=val)
        title = Product.objects.filter(category=product[0].category).values('title')
        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,"app/category.html",locals())
    
@method_decorator(login_required,name='dispatch')
class ProductDetail(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        wishlist = False  # Default to False
        
        if request.user.is_authenticated:
            wishlist = Wishlist.objects.filter(product=product, user=request.user).exists()

        totalitem = 0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        return render(request, "app/productdetail.html", locals())

       
@method_decorator(login_required,name='dispatch')
class CustomerRegistrationView(View):
    def get(self,request):
        form = CustomerRegistrationForm()
        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))
        return render(request,'app/customerregistration.html',locals())
    
    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request,"Congratulation ! User Register Successfully")
        else:
            messages.warning(request,"Invalud Input Data")
        
        return render(request,'app/customerregistration.html',locals())
    
@method_decorator(login_required,name='dispatch')
class ProfileView(View):
    
    def get(self,request):
        form = CustomerProfileForm()
        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        return render(request,'app/profile.html',locals())
    
    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']

            reg = Customer(user=user,name=name,locality=locality,mobile=mobile,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,"Congratulation! Profile Save SuccessFully")
        else:
            messages.warning(request,"Invalid Input Data ")
        return render(request,'app/profile.html',locals())

@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    totalitem=0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/address.html',locals())


@method_decorator(login_required,name='dispatch')
class updateAddress(View):
    def get(self,request,pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)

        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        return render(request,'app/updateAddress.html',locals())
    def post(self,request,pk):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            add = Customer.objects.get(pk=pk)
            add.name = form.cleaned_data['name']
            add.locality = form.cleaned_data['locality']
            add.city = form.cleaned_data['city']
            add.mobile = form.cleaned_data['mobile']
            add.state = form.cleaned_data['state']
            add.zipcode = form.cleaned_data['zipcode']
            add.save()
            messages.success(request,"congratulations! Profile Update Succesfully")

        else:
            messages.warning(request,"Invalid Input Data")

        return redirect("address")
    

@login_required
def add_to_cart(request):
    user=request.user
    product_id=request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()
    return redirect("/cart")


@login_required
def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart:
        value = p.quantity * p.product.discounted_price
        amount = amount + value
    totalamount = amount + 40

    totalitem=0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))
    return render(request,'app/addtocart.html',locals())

@method_decorator(login_required,name='dispatch')
class checkout(View):
    def get(self,request):

        totalitem=0
        wishitem = 0
        if request.user.is_authenticated:
            totalitem = len(Cart.objects.filter(user=request.user))
            wishitem = len(Wishlist.objects.filter(user=request.user))

        user = request.user
        add = Customer.objects.filter(user=user)
        cart_items = Cart.objects.filter(user=user)
        famount = 0
        for p in cart_items:
            value = p.quantity * p.product.discounted_price
            famount = famount + value
        totalamount = famount + 40
        razoramount = int(totalamount*100)
        client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        data = { "amount":razoramount,"currency":"INR","receipt":"order_receipt_11"}
        payment_response = client.order.create(data=data)
        print(payment_response)

        #{'amount': 40000, 'amount_due': 40000, 'amount_paid': 0, 'attempts': 0, 'created_at': 1746247437, 'currency': 'INR', 'entity': 'order', 'id': 'order_QQKQd4m5aoHvxo', 'notes': [], 'offer_id': None, 'receipt': 'order_receipt_11', 'status': 'created'}

        order_id = payment_response['id']
        order_status = payment_response['status']
        if order_status == 'created':
            payment = Payment(
                user = user,
                amount = totalamount,
                razorpay_order_id=order_id,
                razorpay_payment_status =order_status
            )
            payment.save()
        
        return render(request,'app/checkout.html',locals())


@login_required
def orders(request):

    totalitem=0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))

    order_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request,'app/orders.html',locals())


@login_required
def payment_done(request):
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    cust_id = request.GET.get('cust_id')

    user = request.user
    customer = Customer.objects.get(id=cust_id)

    # Fetch payment object using Razorpay order_id
    payment = Payment.objects.get(razorpay_order_id=order_id)

    # Mark payment as 'paid' only if it was successful
    if not payment.paid:  # Only update if not already paid
        payment.paid = True
        payment.razorpay_payment_id = payment_id
        payment.save()

        # To save order details
        cart = Cart.objects.filter(user=user)
        for c in cart:
            # Since payment.paid is True, we consider order as completed
            status = "completed" if payment.paid else "failed"

            # Save the order with payment info
            OrderPlaced(
                user=user,
                customer=customer,
                product=c.product,
                quantity=c.quantity,
                payment=payment,
                status=status
            ).save()
            c.delete()

    return redirect('orders')
  



SHIPPING_CHARGE = 40


@login_required
def calculate_cart_amount(user):
    cart = Cart.objects.filter(user=user)
    amount = sum(p.quantity * p.product.discounted_price for p in cart)
    totalamount = amount + SHIPPING_CHARGE
    return amount, totalamount

@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        if c:
            c.quantity += 1
            c.save()

        amount, totalamount = calculate_cart_amount(request.user)

        return JsonResponse({
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        })


@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        if c and c.quantity > 1:
            c.quantity -= 1
            c.save()

        amount, totalamount = calculate_cart_amount(request.user)

        return JsonResponse({
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': totalamount
        })


@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        c = Cart.objects.filter(Q(product=prod_id) & Q(user=request.user)).first()
        if c:
            c.delete()

        amount, totalamount = calculate_cart_amount(request.user)

        return JsonResponse({
            'amount': amount,
            'totalamount': totalamount
        })


@login_required
def plus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        Wishlist(user=user,product=product).save()
        data={
            'message':'Wishlist Added Successfully...!'
        }
        return JsonResponse(data)

@login_required   
def minus_wishlist(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        product = Product.objects.get(id=prod_id)
        user = request.user
        wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
        if wishlist_item:
            wishlist_item.delete()
        data = {
            'message': 'Wishlist Removed Successfully...!'
        }
        return JsonResponse(data)



@login_required
def search(request):
    query = request.GET['search']
    totalitem = 0
    wishitem = 0
    if request.user.is_authenticated:
        totalitem = len(Cart.objects.filter(user=request.user))
        wishitem = len(Wishlist.objects.filter(user=request.user))

    product = Product.objects.filter(Q(title_icontains=query))

    return render(request,"app/search.html",locals())


@login_required
def show_wishlist(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    return render(request, 'app/wishlist.html', locals())
