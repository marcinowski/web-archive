"""
:created on: 2017-04-24

:author: Marcin Muszynski
:contact: marcinowski007@gmail.com

UseCase: pass url and a path -> generate one compiled html with css classes
"""
import requests
from lxml import etree
from urllib.parse import urlparse


class WebArchiveException(Exception):
    """"""


class WebArchive(object):
    def __init__(self, url, path):
        self.url = url
        self.path = path
        self.session = requests.Session()
        self.html = self._get_content(self.url)
        self.tree = etree.HTML(self.html)
        self.url_parsed = urlparse(self.url)
        self.result_html = ''
        self.css_styles = ''
        self.js_scripts = ''

    def save(self):
        self._handle_links()
        self._handle_styles()
        self._handle_scripts()
        self._insert_elements()
        self._save_file()

    def _handle_links(self):
        for link in self.tree.iter(tag='link'):
            if link.get('rel') == 'stylesheet':
                url = self._resolve_url(link.get('href'))
                self.css_styles += self._get_content(url)
            link.getparent().remove(link)

    def _handle_styles(self):
        for style in self.tree.iter(tag='style'):
            self.css_styles += style.text or ''
            style.getparent().remove(style)

    def _handle_scripts(self):
        for script in self.tree.iter(tag='script'):
            src = script.get('src')
            if not src:
                self.js_scripts += script.text or ''
            else:
                url = self._resolve_url(src)
                self.js_scripts += self._get_content(url)
            script.getparent().remove(script)

    def _insert_elements(self):
        self._insert_element('style', self.css_styles)
        self._insert_element('script', self.js_scripts)

    def _insert_element(self, _tag, content):
        tag = etree.Element(_tag)
        tag.text = content
        self.tree.find('head').append(tag)

    def _save_file(self):
        with open(self.path, 'wb') as f:
            f.write(etree.tostring(self.tree))

    def _resolve_url(self, url):
        if url.startswith('http'):  # absolute url
            return url
        if url.startswith('//'):  # schema relative
            return self.url_parsed.schema + ":" + url
        if url.starstwith('/'):  # relative url
            page_root = self.url_parsed.schema + self.url_parsed.netloc
            return page_root + url
        bwd_path = url.count('../')
        base = list(self.tree.iter(tag='base'))  # 0 or 1
        base_url = base[0].get('href') if base else self.url
        return base_url.rsplit('/', bwd_path)[0] + '/' + url

    def _get_content(self, url):
        try:
            return self._get_response(url)
        except requests.RequestException:
            raise WebArchiveException("Message")
        except AttributeError:
            raise WebArchiveException("Message")

    def _get_response(self, url):
        return self.session.get(url).content.decode()
