"""
Read documents from xhtml
"""

import BeautifulSoup

from pyth import document
from pyth.format import PythReader
from pyth.plugins.xhtml.css import CSS


class XHTMLReader(PythReader):

    @classmethod
    def read(self, source, css_source=None):
        reader = XHTMLReader(source, css_source)
        return reader.go()

    def __init__(self, source, css_source=None):
        self.source = source
        self.css_source = css_source

    def go(self):
        soup = BeautifulSoup.BeautifulSoup(self.source)
        # Make sure the document content doesn't use multi-lines
        soup = self.format(soup)
        doc = document.Document()
        if self.css_source:
            self.css = CSS(self.css_source)
        else:
            self.css = CSS()    # empty css
        self.process_into(soup, doc)
        return doc

    def format(self, soup):
        """format a BeautifulSoup document

        This will transform the block elements content from
        multi-lines text into single line.

        This allow us to avoid having to deal with further text
        rendering once this step has been done.
        """
        # TODO: ignore all new lines just after or before a tag
        for tag in ['p', 'li']:
            for node in soup.findAll(tag):
                text = unicode(node)
                lines = [x.strip() for x in text.splitlines()]
                text = ' '.join(lines)
                node.replaceWith(text)
        return BeautifulSoup.BeautifulSoup(unicode(soup))

    def is_bold(self, node):
        """
        Return true if the BeautifulSoup node needs to be rendered as
        bold.
        """
        return (node.findParent(['b', 'strong']) is not None or
                self.css.is_bold(node))

    def is_italic(self, node):
        """
        Return true if the BeautifulSoup node needs to be rendered as
        italic.
        """
        return node.findParent('em') is not None

    def url(self, node):
        """
        return the url of a BeautifulSoup node or None if there is no
        url.
        """
        a_node = node.findParent('a')
        if not a_node:
            return None
        return a_node.get('href')

    def process_text(self, node):
        """
        Return a pyth Text object from a BeautifulSoup node or None if
        the text is empty.
        """
        assert isinstance(node, BeautifulSoup.NavigableString)
        text = node.string.strip()
        if not text:
            return
        properties=dict()
        if self.is_bold(node):
            properties['bold'] = True
        if self.is_italic(node):
            properties['italic'] = True
        if self.url(node):
            properties['url'] = self.url(node)
        content=[node.string]
        return document.Text(properties, content)

    def process_into(self, node, obj):
        """
        Process a BeautifulSoup node and fill its elements into a pyth
        base object.
        """
        if isinstance(node, BeautifulSoup.NavigableString):
            text = self.process_text(node)
            if text:
                obj.append(text)
            return
        if node.name == 'p':
            # add a new paragraph into the pyth object
            new_obj = document.Paragraph()
            obj.append(new_obj)
            obj = new_obj
        elif node.name == 'ul':
            # add a new list
            new_obj = document.List()
            obj.append(new_obj)
            obj = new_obj
        elif node.name == 'li':
            # add a new list entry
            new_obj = document.ListEntry()
            obj.append(new_obj)
            obj = new_obj
        for child in node:
            self.process_into(child, obj)
