from django.shortcuts import render
from jambalaya.models.models import User


def index(request):
    session = request.db_session
    users = session.query(User)

    data = {user: [user.addresses] for user in users}

    return render(request, "home/index.html", {"dictionary": data})