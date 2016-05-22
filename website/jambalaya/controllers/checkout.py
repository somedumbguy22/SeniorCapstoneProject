from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from jambalaya.models import Category

@login_required
def view_cart(request):
    # Get the user to determine what is in their cart
    user = request.s_user
    cart_contents = []
    for listing in user.cartlistings:
        cart_contents.append(listing)

    return render(request, "checkout/cart.html", {"cart_contents": cart_contents})


def order_details(request, order_id):
    #get the order details of the order using the id
    #session = request.db_session
    #users = session.query(User)

    #data = {user: [user.addresses] for user in users}

    return render(request, "checkout/order_details.html", {"order_id":order_id})#, {"dictionary": data})