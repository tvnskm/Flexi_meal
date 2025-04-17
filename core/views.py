from django.shortcuts import render, redirect
from .models import Meals, Ingredients, Users, Orders, OrderMeals

# Home View
def home_view(request):
    return render(request, 'home.html')

def start_order_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')  # From form input
        address = request.POST.get('address')

        # ✅ Use correct model field name: phone_number
        user = Users.objects.create(name=name, email=email, phone_number=phone, address=address)

        request.session['user_id'] = user.user_id  # Use `user_id` field
        request.session['cart'] = []  # Start with an empty cart

        return redirect('select_meals')

    return render(request, 'start_order.html')


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
        # Retrieve the customized meal and ingredients from the form
        ingredient_quantities = {}
        for ingredient in ingredients:
            ingredient_quantity = request.POST.get(f'ingredient_{ingredient.ingredient_id}', 0)
            if ingredient_quantity:
                ingredient_quantities[ingredient.ingredient_id] = int(ingredient_quantity)

        # Add customized meal to the session cart
        cart = request.session.get('cart', [])

        # Convert Decimal to float for price calculation
        customized_meal = {
            'meal_id': meal.meal_id,
            'name': meal.name,
            'ingredients': ingredient_quantities,
            'quantity': 1,  # Increment by 1 when customized
            'price': float(meal.available_price)  # Convert to float to avoid JSON serialization issue
        }

        # Check if meal is already in the cart
        meal_found = False
        for item in cart:
            if item['meal_id'] == meal.meal_id:
                item['quantity'] += 1  # Increment the quantity if the meal is already in the cart
                meal_found = True
                break

        if not meal_found:
            cart.append(customized_meal)

        # Save the updated cart back to the session
        request.session['cart'] = cart

        # Redirect back to the meal selection page
        return redirect('select_meal')  # Assuming 'select_meal' is your URL name for meal selection

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
            return redirect('order_success', order_id=order.order_id)

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
        return redirect('order_success', order_id=order.order_id)

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
