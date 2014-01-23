from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

class Offices(object):
    implements(IVocabularyFactory)
    def __call__(self, context):
        prop = getToolByName(context, 'portal_properties').ilo_properties
        return SimpleVocabulary.fromValues(prop.officeopts)

class Themes(object):
    implements(IVocabularyFactory)
    def __call__(self, context):
        prop = getToolByName(context, 'portal_properties').ilo_properties
        return SimpleVocabulary.fromValues(prop.themesopts)

