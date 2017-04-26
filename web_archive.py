"""
:created on: 2017-04-24

:author: Marcin Muszynski
:contact: marcinowski007@gmail.com

UseCase: pass url and a path -> generate one compiled html with css classes
"""
import requests
from lxml import etree
from urllib.parse import urlparse


def archive_2(url, path='test.html'):
    try:
        resp = requests.get(url)
    except requests.RequestException:
        return
    css = ''
    html = etree.HTML(resp.content.decode())
    links = filter(lambda tag: tag.get('rel', '') == 'stylesheet', html.iter(tag='link'))
    for l in links:
        u = l.get('href')  # fixme handle relative paths
        r = requests.get(u).content.decode()
        css += '\n' + r
        l.getparent().remove(l)
    for s in html.iter(tag='style'):
        css += s.text or ''
        s.getparent().remove(s)
    scripts = filter(lambda tag: tag.get('src', False), html.iter(tag='script'))
    for s in scripts:
        s.getparent().remove(s)
    s = etree.Element('style')
    s.text = css
    html.find('head').append(s)
    with open(path, 'wb') as f:
        f.write(etree.tostring(html))
