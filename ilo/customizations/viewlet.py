from five import grok
from plone.app.layout.viewlets.interfaces import IPortalTop
from plone.app.layout.viewlets.interfaces import IAboveContent
from zope.interface import Interface
from zope.component import queryUtility, getUtility
#from jarn.xmpp.core.interfaces import IAdminClient
#from jarn.xmpp.core.interfaces import IXMPPUsers
#from jarn.xmpp.twisted.protocols import NS_CLIENT, getRandomId
from Products.CMFCore.utils import getToolByName
#from twisted.words.xish.domish import Element
#from collective.portlet.usertrack.interfaces import ITrackerStorage
from zope.component.hooks import getSite
from time import time
from Products.ILOIntranetTypes.interfaces import IMissionReport
from Products.statusmessages.interfaces import IStatusMessage
class RedirectIfLogged(grok.Viewlet):
    grok.viewletmanager(IPortalTop)
    grok.context(Interface)
    
    def render(self):
        url = self.request.getURL()
        if ('login' in url):
            return ''
        if url.startswith('https://') and (
                not self.context.portal_membership.isAnonymousUser()):
            newurl = url.replace('https://','http://')
            self.request.response.redirect(newurl)
        return ''


class RemindToUsePasteFromWord(grok.Viewlet):
    grok.viewletmanager(IAboveContent)
    grok.context(IMissionReport)

    def render(self):
        if self.view.__name__ == 'at_base_edit_view':
            return u'''
                <div>
                <dl class="portalMessage info"><dt>Pasting from Word?</dt>
                     <dd>
                        Pasting from word can cause some problem with the page formatting.
                        Please use the "Paste from Word" 
                        <img src="pastefromword.gif"/>
                        feature on the editor when pasting from Word.
                    </dd>
                </dl></div>
            '''
        return u''
