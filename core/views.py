from django.shortcuts import render, redirect
from .models import Meals, Ingredients, Users, Orders, OrderMeals
from .forms import OrderForm
# Home View
def home_view(request):
    return render(request, 'home.html')

## def start_order_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # From form input
        address = request.POST.get('address')

      
        user = Users.objects.create(name=name, email=email, phone_number=phone, address=address)

        request.session['user_id'] = user.user_id  # Use `user_id` field
        request.session['cart'] = []  # Start with an empty cart

        return redirect('select_meals')

    return render(request, 'start_order.html') 

from .forms import OrderForm

def start_order_view(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']

            user = Users.objects.create(
                name=name,
                email=email,
                phone_number=phone,
                address=address
            )

            request.session['user_id'] = user.user_id
            request.session['cart'] = []

            return redirect('select_meals')
        else:
            # Re-render form with error messages
            return render(request, 'start_order.html', {'form': form})

    else:
        form = OrderForm()
    return render(request, 'start_order.html', {'form': form})

# Select Meals View
def select_meals_view(request):
    meals = Meals.objects.all()
    user_id = request.session.get('user_id')

    if request.method == 'POST':
        meal_id = request.POST.get('meal_id')
        if meal_id:
            meal_id = int(meal_id)
            # Redirect to the customization page
            return redirect('customize_meal', meal_id=meal_id)

    cart_count = len(request.session.get('cart', []))
    return render(request, 'select_meals.html', {'meals': meals, 'cart_count': cart_count})
# Cart View
from .models import Meals  # Ensure Meals model is correctly imported

from django.shortcuts import render, redirect
from .models import Meals, Ingredients
from django.http import HttpResponse

def customize_meal_view(request, meal_id):
    meal = Meals.objects.get(meal_id=meal_id)
    ingredients = Ingredients.objects.all()

    if request.method == 'POST':
        ingredient_quantities = {}
        additional_cost = 0

        for ingredient in ingredients:
            qty_str = request.POST.get(f'ingredient_{ingredient.ingredient_id}', '0')
            quantity = int(qty_str) if qty_str.isdigit() else 0

            if quantity > 0:
                ingredient_quantities[ingredient.ingredient_id] = quantity
                additional_cost += quantity * float(ingredient.price)  # using 'price' field

        cart = request.session.get('cart', [])

        customized_price = float(meal.available_price) + additional_cost

        customized_meal = {
            'meal_id': meal.meal_id,
            'name': meal.name,
            'ingredients': ingredient_quantities,
            'quantity': 1,
            'price': round(customized_price, 2)
        }

        cart.append(customized_meal)
        request.session['cart'] = cart

        return redirect('select_meals')  # Update with your actual meal selection URL name

    return render(request, 'customize_meal.html', {'meal': meal, 'ingredients': ingredients})




def cart_view(request):
    cart = request.session.get('cart', [])
    cart_items = []
    total_price = 0

    # Gather the items in the cart
    for item in cart:
        meal = Meals.objects.get(meal_id=item['meal_id'])
        cart_items.append({
            'meal_id': meal.meal_id,
            'name': meal.name,
            'quantity': item['quantity'],
            'price': meal.available_price,
            'total_price': item['quantity'] * float(meal.available_price)
        })
        total_price += item['quantity'] * float(meal.available_price)

    # When POST is received, confirm the order
    if request.method == 'POST':
        # Make sure user is logged in and cart is not empty
        user_id = request.session.get('user_id')
        if user_id and cart:
            user = Users.objects.get(user_id=user_id)

            # Create the order for the user
            order = Orders.objects.create(
                user=user,
                order_date=timezone.now(),
                total_price=total_price,
                status='Pending'  # You can set it to 'Pending' or another status
            )

            # Add the meals to the order
            for item in cart:
                meal = Meals.objects.get(meal_id=item['meal_id'])
                OrderMeals.objects.create(order=order, meal=meal, quantity=item['quantity'])

            # Clear the session cart after order is created
            request.session['cart'] = []

            # Redirect to the order success page with the order ID
            return redirect('payment', order_id=order.order_id)

    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout_view(request):
    # Placeholder view, you can add checkout logic here
    return render(request, 'checkout.html')

from django.shortcuts import render, redirect
from .models import Orders, OrderMeals, Meals, Users
from django.utils import timezone

def confirm_order_view(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        cart = request.session.get('cart', [])

        # Ensure user is logged in and cart is not empty
        if not user_id or not cart:
            return redirect('start_order')  # If no user or cart, redirect to start_order page

        # Create a new order for the user
        user = Users.objects.get(user_id=user_id)
        order = Orders.objects.create(user=user, order_date=timezone.now(), total_price=0)  # Creating the order

        total_price = 0  # To track total price of the order

        # Add each item from the cart to the order
        for item in cart:
            meal = Meals.objects.get(meal_id=item['meal_id'])
            total_price += item['quantity'] * float(meal.available_price)
            OrderMeals.objects.create(order=order, meal=meal, quantity=item['quantity'])

        # Update the total price for the order
        order.total_price = total_price
        order.save()

        # Clear the session cart after the order is created
        request.session['cart'] = []

        # Redirect to the order success page with the order ID
        return redirect('payment', order_id=order.order_id)


    # If method is not POST, redirect to the cart page
    return redirect('cart')

# View for the success page after the order is confirmed
def order_success_view(request, order_id):
    # Retrieve the order using the order_id from the URL
    order = Orders.objects.get(order_id=order_id)
    order_meals = OrderMeals.objects.filter(order=order)

    return render(request, 'order_success.html', {'order': order, 'order_meals': order_meals})




def user_list_view(request):
    users = Users.objects.all()  # Fetch all users
    return render(request, 'user_list.html', {'users': users})

# views.py
def user_orders_view(request, user_id):
    # Get the user object
    user = Users.objects.get(user_id=user_id)
    
    # Get all orders for this user
    orders = Orders.objects.filter(user_id=user).order_by('-order_date')
    
    return render(request, 'user_orders.html', {'user': user, 'orders': orders})

from .models import Payments

def payment_view(request, order_id):
    order = Orders.objects.get(order_id=order_id)

    if request.method == 'POST':
        method = request.POST.get('payment_method')
        card_number = request.POST.get('card_number', '').strip()
        upi_id = request.POST.get('upi_id', '').strip()

        # Basic validation based on method
        if method == 'card' and (not card_number or len(card_number) != 16 or not card_number.isdigit()):
            return render(request, 'payment.html', {
                'order': order,
                'error': 'Please enter a valid 16-digit card number.'
            })

        if method == 'upi' and ('@' not in upi_id or len(upi_id) < 5):
            return render(request, 'payment.html', {
                'order': order,
                'error': 'Please enter a valid UPI ID.'
            })

        # Save payment
        Payments.objects.create(
            order=order,
            method=method,
            card_number=card_number if method == 'card' else None,
            upi_id=upi_id if method == 'upi' else None
        )

        # Update order status
        order.status = 'Confirmed'
        order.save()

        return redirect('order_success', order_id=order.order_id)

    return render(request, 'payment.html', {'order': order})

