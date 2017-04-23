# -*- coding: utf-8 -*-
'''
Created on 2014-06-30
@summary: render search result
@author: YangHaitao
'''

import tornado.web
import logging
import math
import re
import urlparse
import urllib
from utils.html import add_params_to_url

# import chardet


from config import CONFIG

LOG = logging.getLogger(__name__)


class ThumbnailCollections(tornado.web.UIModule):
    def render(self, elements):
        '''
          @summary: construct Thumbnail Collections
          @param elements: a list of ThumbnailItem
          @param column_count: count of the column
          @result:
        '''
        def construct_li(element):
            description1, description2 = element.description.split("\n\n")
            html = ""
            html += '<li class="item_li item_well">'
            html += '<a id="item" href = %s target="_blank"><p class="item_name">%s</p></a>'%(element.url, element.text)
            html += '<div class="item_excerpts_div"><p class="item_excerpts">' + element.excerpts + '</p></div>'
            html += '<p class="item_description">' + description1 + '<br>' + description2 + '</p>'
            html += "</li>"
            return html

        html = ''
        html +='<ul class="list-unstyled">'
        for element in elements:
            html += construct_li(element)
        html += '</ul>'
        return html

class Paginator(tornado.web.UIModule):
    '''
    @summary: create paginator

    '''
    def render(self, total_count, search_time, min_time, max_time, current_page = 0, items_per_page = 10, url =""):
        '''
        @summary:

        @param total_page: total page number
        @param current_page: current page number

        @result:
        '''
        def format_li(url, page_number, active = False):
            url_tmp = ""
            url_tmp = add_params_to_url(url, dict({"page": page_number}))
            if active:
                return "<li class=\"active\"><a href=\"%s\">%s</a></li>\n" %(url_tmp, page_number)
            else:
                return "<li><a href=\"%s\">%s</a></li>\n" %(url_tmp, page_number)

        if search_time == 'Custom_date_range':
            url += "&min_time=%s&max_time=%s"%(min_time, max_time)
        if total_count <=0:
            return ""
        # when there is only one page, not need to display the paginator
        total_page = int(math.ceil(total_count * 1.0/ items_per_page))
        if total_page <= 1:
            return ""

        html = ""
        html = "<div id='paginator' class='row'>\n"
        html += "<ul class=\"pagination\">\n"
        max_pages_pre = 5
        max_pages_post = 4

        if current_page <= max_pages_pre:
            max_pages_pre = current_page - 1
        if current_page + max_pages_post >= total_page:
            max_pages_post = total_page - current_page

        if current_page > 1:
            url_pre_page = add_params_to_url(url, dict({"page": current_page - 1}))
            html += "<li><a href=\"%s\">&laquo;</a></li>\n"%(url_pre_page,)

        # construct previous page links
        for i in xrange(max_pages_pre):
            html += format_li(url, current_page - max_pages_pre + i)
        # construct current page link
        html += format_li(url, current_page, True)
        # construct post page links
        for i in xrange(max_pages_post):
            html += format_li(url, current_page + 1 + i)
        # construct next page link
        if current_page < total_page - 1:
            url_next_page = add_params_to_url(url, dict({"page": current_page + 1}))
            html += "<li><a href=\"%s\">&raquo;</a></li>\n"%(url_next_page,)
        html += "</ul>\n"
        html += "</div>\n"
        return html

class JsString(tornado.web.UIModule):
    '''
    @summary: create a javascript string

    '''
    def escape_string(self, string):
        return re.sub(r"([\"\'\\])", r"\\\1", string)

    def render(self, js_str):
        js_str = self.escape_string(js_str)
        return js_str.encode("utf-8")