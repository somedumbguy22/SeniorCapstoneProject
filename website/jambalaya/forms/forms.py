from django.forms import Form, CharField, FileField, ChoiceField, IntegerField, FloatField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from crispy_forms.bootstrap import PrependedText
from django.core.urlresolvers import reverse

from jambalaya.forms.widgets import CategoryChooser


class HorizontalFormBase(Form):
    def __init__(self, *args, **kwargs):
        super(HorizontalFormBase, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'


class CreateListingForm(HorizontalFormBase):
    def __init__(self, *args, **kwargs):
        self.is_seller = kwargs.pop("is_seller")
        self.item_id = kwargs.pop("item_id")

        super(CreateListingForm, self).__init__(*args, **kwargs)
        self.helper.form_action = reverse("list_item", kwargs={"item_id": self.item_id})
        self.helper.add_input(Submit('submit', 'Create'))
        self.helper.layout = Layout(
            Field("condition"),
            PrependedText("website", "http://"),
            Field("is_auction"),
            Div(
                Field("quantity"),
                PrependedText("direct_sale_price", "$"),
                css_id="direct_sale_group"),
            Div(
                PrependedText("auction_min_price", "$"),
                css_id="auction_group")
        )

        if not self.is_seller:
            self.fields["is_auction"].initial = 1
            self.fields["is_auction"].choices = [(1, "Auction")]
            self.fields["is_auction"].widget.attrs = {"data-toggle": "tooltip",
                                                      "data-placement": "top",
                                                      "title": "Sorry, but you must have a seller account to list direct sale items"}

    condition = ChoiceField(label="Condition", choices=[(0, "New"), (1, "Used")])
    website = CharField(label="Seller website", max_length=255)
    is_auction = ChoiceField(label="Type of listing", choices=[(0, "Direct sale"), (1, "Auction")])

    quantity = IntegerField(label="Quantity available", min_value=1, initial=1)
    direct_sale_price = FloatField(label="Price", initial=0.01, min_value=0.01)
    auction_min_price = FloatField(label="Minimum price", initial=2, min_value=2)


class CreateItemForm(HorizontalFormBase):
    def __init__(self, *args, **kwargs):
        self.categories = kwargs.pop("categories", [])
        self.selected_category = kwargs.pop("selected_category", None)

        super(CreateItemForm, self).__init__(*args, **kwargs)
        self.helper.form_action = 'create_item'
        self.helper.add_input(Submit('submit', 'Continue'))

        self.fields["item_name"] = CharField(label="Item name", max_length=255)
        self.fields["description"] = CharField(label="Description")
        self.fields["category"] = CategoryChooser(label="Category", categories=self.categories,
                                                  initial=self.selected_category)
        self.fields["image"] = FileField(label="Product image", required=False)