# -*- coding: utf-8 -*-
"""
Translator module that uses the Google Translate API.

Adapted from Terry Yin's google-translate-python.
Language detection added by Steven Loria.
"""
from __future__ import absolute_import
import json
import re
import codecs
from textblob.compat import PY2, request, urlencode
from textblob.exceptions import TranslatorError


class Translator(object):

    """A language translator and detector.

    Usage:
    ::
        >>> from textblob.translate import Translator
        >>> t = Translator()
        >>> t.translate('hello', from_lang='en', to_lang='fr')
        u'bonjour'
        >>> t.detect("hola")
        u'es'
    """

    url = "http://translate.google.com/translate_a/t"

    headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) '
            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.168 Safari/535.19')}

    def translate(self, source, from_lang=None, to_lang='en', host=None, type_=None):
        """Translate the source text from one language to another."""
        if PY2:
            source = source.encode('utf-8')
        data = {"client": "p", "ie": "UTF-8", "oe": "UTF-8",
                "sl": from_lang, "tl": to_lang, "text": source}
        json5 = self._get_json5(self.url, host=host, type_=type_, data=data)
        return self._get_translation_from_json5(json5)

    def detect(self, source, host=None, type_=None):
        """Detect the source text's language."""
        if PY2:
            source = source.encode('utf-8')
        if len(source) < 3:
            raise TranslatorError('Must provide a string with at least 3 characters.')
        data = {"client": "p", "ie": "UTF-8", "oe": "UTF-8", "text": source}
        json5 = self._get_json5(self.url, host=host, type_=type_, data=data)
        lang = self._get_language_from_json5(json5)
        return lang

    def _get_language_from_json5(self, content):
        json_data = json.loads(content)
        if 'src' in json_data:
            return json_data['src']
        return None

    def _get_translation_from_json5(self, content):
        result = u""
        json_data = json.loads(content)
        if 'sentences' in json_data:
            result = ''.join([s['trans'] for s in json_data['sentences']])
        return _unescape(result)

    def _get_json5(self, url, host=None, type_=None, data=None):
        encoded_data = urlencode(data).encode('utf-8')
        req = request.Request(url=url, headers=self.headers, data=encoded_data)
        if host or type_:
            req.set_proxy(host=host, type=type_)
        resp = request.urlopen(req)
        content = resp.read()
        return content.decode('utf-8')


def _unescape(text):
    """Unescape unicode character codes within a string.
    """
    pattern = r'\\{1,2}u[0-9a-fA-F]{4}'
    decode = lambda x: codecs.getdecoder('unicode_escape')(x.group())[0]
    return re.sub(pattern, decode, text)
