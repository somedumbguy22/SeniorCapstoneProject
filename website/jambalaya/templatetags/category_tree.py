from django import template
from django.template.loader import render_to_string
from jambalaya.models import Category
from django.core.urlresolvers import reverse
import json

register = template.Library()


@register.simple_tag(takes_context=True)
def category_tree(context, active=None):
    """
    Produces the HTML and JavaScript necessary to create a category tree for navigation.
    :param context: Django context object (automatically provided by context provider)
    :param active: The ID of the active category, or None if not selected
    :return: Returns the HTML/JavaScript that is directly pasted into the calling template
    """
    if active:
        active = int(active)

    # This function generates an object in the format that bootstrap-treeview expects for every node
    def visitor(node, item_count, children):
        ret = {"text": node.Name, "id": node.ID}

        if children:
            ret["selectable"] = False
            ret["nodes"] = children
        elif item_count > 0:
            ret["tags"] = [item_count]

        ret["state"] = {}
        if active and (active == node.ID):
            if children:
                ret["state"]["expanded"] = True
            else:
                ret["state"]["selected"] = True

        ret["href"] = reverse("browse_category", args=(node.ID, node.Name.replace(" ", "-").lower()))
        return ret

    data, parent_to_child = Category.eager_load_tree(context["request"].db_session, visitor_fn=visitor)

    # Need to expand the parent nodes of the selected category
    if active:
        # Inverse the mapping of parents => children
        child_to_parent = {v[0].ID: k for k in parent_to_child for v in parent_to_child[k]}

        # Walk from child => top level parent and build path as we go
        path = set()
        current = active
        while current in child_to_parent:
            path.add(current)
            current = child_to_parent[current]
        path.add(current)
        if len(path) == 1:
            path = set()

        # Follow the path we just found and mark nodes expanded
        next_nodes = data
        while path:
            next_nodes = [node for node in next_nodes if node["id"] in path]
            this_node = next_nodes[0]
            path.remove(this_node["id"])
            this_node["state"]["expanded"] = True
            next_nodes = this_node["nodes"] if "nodes" in this_node else []

    data = json.dumps(data)
    return render_to_string("internal/category_tree.html", {"data": data})