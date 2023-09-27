from django import template
from django.contrib.admin.templatetags.base import InclusionAdminNode
from django.contrib.admin.templatetags.admin_list import result_list
from django.contrib.admin.templatetags.admin_modify import submit_row
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.admin.views.main import PAGE_VAR
import re


register = template.Library()

@register.tag(name="table")
def table(parser, token):
  return InclusionAdminNode(parser, token, func=result_list, template_name='change_list_results.html', takes_context=False)

@register.simple_tag
def paginator_number(cl, i):
    """
    Generate an individual page index link in a paginated list.
    """
    if i == cl.paginator.ELLIPSIS:
        return format_html('<li class="page-item"><a class="page-link" href="#">{}</a></li>', cl.paginator.ELLIPSIS)
    elif i == cl.page_num:
        return format_html('<li class="page-item active"><a class="page-link" href="#">{}</a></li>', i) 
    else:
        return format_html(
            '<li class="page-item"><a class="page-link" href="{}"{}>{}</a></li>',
            cl.get_query_string({PAGE_VAR: i}),
            mark_safe(' class="end"' if i == cl.paginator.num_pages else ""),
            i,
        )

@register.tag(name="submit_row_bs5")
def submit_row_tag(parser, token):
    return InclusionAdminNode(
        parser, token, func=submit_row, template_name="submit_line.html"
    )

@register.filter
def get_length(obj):
    return len(obj.fields)

@register.filter
def get_half(obj):
    if len(obj.fields) > 1:
        return int(len(obj.fields) / 2)
    else:
        return int(len(obj.fields) / 2) + 1

@register.filter
def bs5_label(obj):
    regex = r'<label(.*?)for="id_(.*?)">(.*?)</label>'
    regex2 = r'<label>(.*?)</label>'
    regex3 = r'<label(.*?)>(.*?)</label>'
    regex4 = r'<input type="text"(.*?)class="vTextField(.*?)">'

    subst = r'<label class="form-label" for="id_\2">\3</label>'
    subst2 = r'<label class="form-label">\1</label>'
    subst3 = r'<label class="form-label">\2</label>'
    subst4 = r'<input type="text"\1class="form-control\2">'

    obj = re.sub(regex, subst, obj)
    obj = re.sub(regex2, subst2, obj)
    obj = re.sub(regex3, subst3, obj)
    obj = re.sub(regex4, subst4, obj)

    return obj

@register.filter
def bs5_checkbox(obj):
    # Add class checkbox of bs5 to BoundField 
    obj.field.widget.attrs['class'] = 'form-check-input'
    return obj

@register.filter
def bs5_checkbox_label(obj):
    regex = r'<label(.*?)for="id_(.*?)">(.*?)</label>'
    subst = r'<label class="form-check-label" for="id_\2">\3</label>'
    obj = re.sub(regex, subst, obj)
    return obj

@register.filter
def bs5_input(obj):
    # check if input has class vTextField (object is BoundField)
    if 'class' in obj.field.widget.attrs:
        if obj.field.widget.attrs['class'] == 'vTextField' or obj.field.widget.attrs['class'] == 'vIntegerField':
            obj.field.widget.attrs['class'] = 'form-control'
    return obj
