from django import template

register = template.Library()

@register.inclusion_tag('includes/product_card.html')
def product_card(product, list_view=False, with_cart_button=True):
    return {
        'product': product,
        'list_view': list_view,
        'with_cart_button': with_cart_button
    }

@register.inclusion_tag('includes/product_list_item.html')
def product_list_item(product):
    return {'product': product}