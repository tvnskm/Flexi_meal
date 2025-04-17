from django.db import models

class Ingredients(models.Model):
    ingredient_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    proteins = models.DecimalField(max_digits=5, decimal_places=2)
    carbs = models.DecimalField(max_digits=5, decimal_places=2)
    fibre = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'ingredients'


class Meals(models.Model):
    meal_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    available_price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.ManyToManyField(Ingredients, through='MealIngredient')

    class Meta:
        db_table = 'meals'


class MealIngredient(models.Model):
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2)  # e.g., in grams

    class Meta:
        db_table = 'meal_ingredients'
        unique_together = ('meal', 'ingredient')


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    class Meta:
        db_table = 'users'


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'


class OrderMeals(models.Model):
    order_meal_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    class Meta:
        db_table = 'order_meals'


class MealCustomization(models.Model):
    meal = models.ForeignKey(Meals, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredients, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    special_instructions = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'meal_customizations'


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'payment'
