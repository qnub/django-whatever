# -*- coding: utf-8 -*-
from django import forms
from django_any import any_form
from django.test.client import Client as DjangoClient
from django_any.contrib.auth import any_user
from django.contrib.admin.helpers import AdminForm
from django_any import xunit

def _request_context_forms(context):
    """
    Lookup all stored in context froms instance
    """
    if isinstance(context, list):
        dicts = context[0].dicts
    else:
        dicts = context.dicts

    for context in dicts:
        for _, inst in context.items():
            if isinstance(inst, forms.Form):
                yield inst
            elif isinstance(inst, AdminForm):
                yield inst.form


class Client(DjangoClient):
    def login_as(self, **kwargs):
        password = xunit.any_string()
        user = any_user(password=password, **kwargs)

        if self.login(username=user.username, password=password):
            return user
        raise AssertionError('Can''t login with autogenerated user')

    def post_any_data(self, url, extra=None, context_forms=_request_context_forms, **kwargs):
        request = self.get(url)

        post_data = {}

        #TODO support string and list of strings as forms names in context
        for form in context_forms(request.context):
            form_data, form_files = any_form(form.__class__) #TODO support form instance

            if form.prefix:
                form_data = dict([('%s-%s' % (form.prefix, key), value) for key, value in form_data.items()])

            post_data.update(form_data)

        if extra:
            post_data.update(extra)

        return self.post(url, post_data)
