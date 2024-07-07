from django.core.paginator import Paginator, Page
from django.utils.functional import cached_property
from django.core.paginator import EmptyPage, PageNotAnInteger
from math import ceil
import requests
from .get_json_api import get_car
import datetime


class CustomPaginator(Paginator):
    def __init__(self, count, per_page, api_url, table, filter, ip, page_number):
        super().__init__([], per_page)
        self.api_url = api_url
        self.table = table
        self.filter = filter
        self._count = count
        self.ip = ip
        self.page_number = page_number

    def _get_page(self, *args, **kwargs):
        page_number = args[1]
        offset = (page_number - 1) * self.per_page
        
        url = self.api_url.format(
            table=self.table,
            filter=self.filter,
            limit=self.per_page,
            offset=offset,
            ip=self.ip,
        )
        
        res_text = requests.get(url).text
        queryset = self.processing_data(res_text)
        return Page(queryset, page_number, self)

    @cached_property
    def num_pages(self):
        if self._count == 0 and not self.allow_empty_first_page:
            return 0
        hits = max(1, self._count - self.orphans)
        return ceil(hits / self.per_page)

    def processing_data(self, response_text):
        return get_car(response_text, self.table)


def get_page(paginator: Paginator, page_number):
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj
