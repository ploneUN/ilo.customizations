from collective.pdfexport.interfaces import IPDFEmailSource
from five import grok
from zope.interface import Interface
from plone.memoize import ram
from time import time
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from plone import api
import ldap

class PDFEmailSource(grok.Adapter):
    grok.context(Interface)
    grok.implements(IPDFEmailSource)
    grok.name('ldap')

    def __init__(self, context):
        self.ldapobj = ldap.initialize('ldap://ldap.bkk.ilo.vg:389')
        self.context = context

    @ram.cache(lambda *args: 'LDAPSource%s' % (time() // (60 * 60)))
    def options(self):
        r = self.ldapobj.search_s('o=ILO',
                ldap.SCOPE_SUBTREE, '(objectClass=*)', ['mail'])
        result = []
        for dn, entry in r:
            result.append(entry['mail'][0].lower().strip())
        return [
            {'value': 'LDAPEmail:%s' % v, 'title': v} for v in result
        ]

    def can_expand(self, value):
        return value.startswith('LDAPEmail:')

    def expand_value(self, value):
        email = value.replace('LDAPEmail:','')
        if not email:
            return []
        return [email]

    def search(self, query):
        options = self.options()
        return [
            v for v in options if query.lower() in v['title'].lower()
        ]


