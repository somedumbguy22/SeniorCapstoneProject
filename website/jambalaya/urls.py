from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = patterns("",
    url(r"^$", "jambalaya.controllers.home.index", name="home"),
    url(r"^browse/(?P<category_id>\d+)-(?P<category_name>.*)$", "jambalaya.controllers.item.browse", name="browse_category"),

    url(r'^cart/$', "jambalaya.controllers.checkout.view_cart", name="view_cart"),
    url(r'^order_details/(?P<order_id>\d+)$', "jambalaya.controllers.checkout.order_details", name="order_details"),

    # Note: If you change name="login" below, be sure to update UsernameLookupMiddleware
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'auth/login.html'}, name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    #url(r'^accounts/profile/(?P<user_id>\d+)$', "jambalaya.controllers.accounts.profile", name="profile"),
    url(r'^profile/$', "jambalaya.controllers.accounts.profile", name="profile"),

    url(r'search/$', "jambalaya.controllers.search.search", name="search"),

    url(r"^items/create/(?P<category_id>\d+)?$", "jambalaya.controllers.item.create", name="create_item"),
    url(r"^items/list/(?P<item_id>\w+)$", "jambalaya.controllers.listing.create", name="list_item"),
    url(r"^items/(?P<item_id>\w+)$", "jambalaya.controllers.item.view", name="view_item"),
    url(r"^help/$", TemplateView.as_view(template_name="Other/help.html"), name="help"),
    url(r'hot_items/$', "jambalaya.controllers.hot_items.getHotItems", name="hot_items"),
    url(r'recently_viewed/$', "jambalaya.controllers.recently_viewed_items.recentlyViewedItems", name="recently_viewed")
)
