from itertools import chain

from django.forms import ChoiceField
from django.forms.widgets import Widget
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt


class CategoryChooser(ChoiceField):
    def __init__(self, *args, **kwargs):
        self.valid_choices = []
        categories = kwargs.pop("categories", [])
        kwargs["widget"] = NestedSelect()
        kwargs["choices"] = self._build_tree(categories)
        super(CategoryChooser, self).__init__(*args, **kwargs)

    def _build_tree(self, entries):
        ret = []
        for entry in entries:
            if entry["children"]:
                ret.append((entry["category"].Name, self._build_tree(entry["children"])))
            else:
                self.valid_choices.append(entry["category"].ID)
                ret.append((entry["category"].ID, entry["category"].Name))
        return ret

    def validate(self, value):
        return value in self.valid_choices

    def to_python(self, value):
        return long(value)


class NestedSelect(Widget):
    allow_multiple_selected = False

    def __init__(self, attrs=None, choices=()):
        super(NestedSelect, self).__init__(attrs)
        # choices can be any iterable, but we may need to render this widget
        # multiple times. Thus, collapse it into a list so it can be consumed
        # more than once.
        self.choices = list(choices)

    def render(self, name, value, attrs=None, choices=()):
        final_attrs = self.build_attrs(attrs, name=name)
        output = [format_html('<select{}>', flatatt(final_attrs))]
        selected_choices = set(force_text(v) for v in [value])
        options = '\n'.join(self.process_list(selected_choices, chain(self.choices, choices)))
        if options:
            output.append(options)
        output.append('</select>')
        return mark_safe('\n'.join(output))

    def render_group(self, selected_choices, option_value, option_label, level=0):
        padding = "&nbsp;" * (level * 4)
        output = format_html("<option disabled>%s{}</option>" % padding, force_text(option_value))
        output += "".join(self.process_list(selected_choices, option_label, level + 1))
        return output

    def process_list(self, selected_choices, l, level=0):
        output = []
        for option_value, option_label in l:
            if isinstance(option_label, (list, tuple)):
                output.append(self.render_group(selected_choices, option_value, option_label, level))
            else:
                output.append(self.render_option(selected_choices, option_value, option_label, level))
        return output

    def render_option(self, selected_choices, option_value, option_label, level):
        padding = "&nbsp;" * (level * 4)
        if option_value is None:
            option_value = ''
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''
        return format_html('<option value="{}"{}>%s{}</option>' % padding, option_value, selected_html,
                           force_text(option_label))