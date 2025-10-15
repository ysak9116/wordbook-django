from django import template

register = template.Library()


@register.filter
def add_class(field, css):
    # 既存クラスを保ったまま追加
    attrs = field.field.widget.attrs
    attrs["class"] = (attrs.get("class", "") + " " + css).strip()
    return field.as_widget(attrs=attrs)
