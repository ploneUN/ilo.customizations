import logging
logger = logging.getLogger('ilo.customization.patches')


def apply_patches():
    _apply_inigo_PlonePAS_testMemberData()
#    _apply_mlarchive_patch()
    _apply_registration_validate_patch()
    _apply_quickupload_browservar_patch()
    apply_localsitemap_path()
    _apply_unauthorized_binding_patch()
#    _apply_safeId_patch()
    _apply_fix_member_portrait()
    _apply_comment_src_patch()
    _apply_formlib_ignore_missing_vocab()
    _apply_collectivesolr_facetednav_compat()
    _apply_xmppcore_lowercase_postNode()
    _apply_eea_empty_folder_hack()
    _apply_remove_integer_grouping()
    _apply_wrap_broken_blobgetfilename()
    _patch_solgema_data_extender()

def _apply_formlib_ignore_missing_vocab():
    try:
        from zope.formlib.itemswidgets import OrderedMultiSelectWidget
    except:
        return

    patched = getattr(OrderedMultiSelectWidget,
            '__inigo_ignoremissing_patched', False)

    if patched: return


    def selected(self):
        """Return a list of tuples (text, value) that are selected."""
        # Get form values
        values = self._getFormValue()
        # Not all content objects must necessarily support the attributes
        if hasattr(self.context.context, self.context.__name__):
            # merge in values from content
            for value in self.context.get(self.context.context):
                if value not in values:
                    values.append(value)

        terms = []
        for value in values:
            try:
                term = self.vocabulary.getTerm(value)
            except:
                continue
            terms.append(term)

        return [{'text': self.textForValue(term), 'value': term.token}
                for term in terms]

    OrderedMultiSelectWidget.selected = selected

    OrderedMultiSelectWidget.__inigo_ignoremissing_patched = True


def apply_localsitemap_path():
    try:
        from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
    except:
        return

    patched = getattr(SitemapQueryBuilder, '__inigo_localsitemap_patched',
            False)

    if patched:
        return

    from Products.CMFCore.utils import getToolByName
    orig = SitemapQueryBuilder.__init__
    def __init__(self, context):
        orig(self, context)
        self.query['path']['query'] = '/'.join(context.getPhysicalPath())

    SitemapQueryBuilder.__init__ = __init__

    SitemapQueryBuilder.__inigo_localsitemap_patched = True

def _apply_inigo_PlonePAS_testMemberData():
    try:
        import Products.PlonePAS.plugins.property
    except:
        return 

    patched = getattr(Products.PlonePAS.plugins.property,'__inigo_testMemberData_patched',False)

    if patched:
       return

    from Products.PlonePAS.plugins.property import isStringType

    Products.PlonePAS.plugins.property.ZODBMutablePropertyProvider.__inigo_orig_testMemberData = Products.PlonePAS.plugins.property.ZODBMutablePropertyProvider.testMemberData

    logger.info("MonkeyPatching ZODBMutablePropertyProvider.testMemberData")
    
    def testMemberData(self, memberdata, criteria, exact_match=False):
        """Test if a memberdata matches the search criteria.
        """
        for (key, value) in criteria.items():
            testvalue=memberdata.get(key, None)
            if testvalue is None:
                return False

            if isStringType(testvalue):
                testvalue=testvalue.lower()
            else:
                try:
                    testvalue = [ subval.lower() for subval in testvalue ]
                except TypeError:
                    pass

            if isStringType(value):
                value=value.lower()
            else:
                try:
                    value = [ subval.lower() for subval in value ]
                except TypeError:
                    pass
                
            if exact_match:
                if value!=testvalue:
                    return False
            else:
                if (not isStringType(testvalue)) and (not isStringType(value)):
                   try:
                      for subval in value:
                           if subval in testvalue:
                              return True
                   except TypeError:
                      pass

                try:
                    if value not in testvalue:
                        return False
                except TypeError:
                    # Fall back to exact match if we can check for sub-component
                    if value!=testvalue:
                        return False


        return True

    Products.PlonePAS.plugins.property.ZODBMutablePropertyProvider.testMemberData = testMemberData
    Products.PlonePAS.plugins.property.__inigo_testMemberData_patched = True


def _apply_registration_validate_patch():
    from Products.CMFPlone.RegistrationTool import RegistrationTool
    from Products.CMFCore.utils import getToolByName
    from zope.security import checkPermission
    if getattr(RegistrationTool, '__inigo_registration_patched', False):
        return

    _orig_isValidEmail = RegistrationTool.isValidEmail
    def isValidEmail(self, email):
        result = _orig_isValidEmail(self, email)
        mtool = getToolByName(self, 'portal_membership')

        if not mtool.isAnonymousUser():
            member = mtool.getAuthenticatedMember()
            if member.getProperty('email') == email:
                return result
            if checkPermission('cmf.ManagePortal', self):
                return result

        if result:
            if not (email.endswith('@ilo.org') or
                    email.endswith('@itcilo.org') or
                    email.endswith('@betterwork.org') or 
                    email.endswith('@iloguest.org')):
                return 0
        return 1

    RegistrationTool.isValidEmail = isValidEmail
    RegistrationTool.__inigo_registration_patched = True


def _apply_quickupload_browservar_patch():
    from collective.quickupload.portlet import quickuploadportlet

    if getattr(quickuploadportlet, '__inigo_browservar_patched', False):
        return 

    quickuploadportlet.JAVASCRIPT = quickuploadportlet.JAVASCRIPT.replace('var Browser = {};', '''
    if (typeof(Browser) == 'undefined') {
        var Browser = {};
    }
    ''')

    quickuploadportlet.__inigo_browservar_patched = True


def _apply_unauthorized_binding_patch():
    from plone.app.portlets.manager import PortletManagerRenderer

    if getattr(PortletManagerRenderer, '__inigo_unauth_patched', False):
        return

    from Shared.DC.Scripts.Bindings import UnauthorizedBinding
    from AccessControl import Unauthorized
    
    _orig_dataToPortlet = PortletManagerRenderer._dataToPortlet

    def _dataToPortlet(self, data):
        if isinstance(self.context, UnauthorizedBinding):
            raise Unauthorized
        return _orig_dataToPortlet(self, data)
    PortletManagerRenderer._dataToPortlet = _dataToPortlet
    PortletManagerRenderer.__inigo_unauth_patched = True

    
def _apply_safeId_patch():
    from Products.PlonePAS.tools.membership import MembershipTool
    
    if getattr(MembershipTool, '__inigo_safeId_patched', False):
        return

    _orig_getSafeMemberId = MembershipTool._getSafeMemberId

    def _getSafeMemberId(self, id=None):
        result = _orig_getSafeMemberId(self, id)
        return result.replace('-40','@')

    MembershipTool._getSafeMemberId = _getSafeMemberId
    MembershipTool.__inigo_safeId_patched = True



def _apply_fix_member_portrait():
    from OFS.Image import Image
    from Products.CMFCore.utils import getToolByName
    from Products.PlonePAS.tools.membership import MembershipTool
    from Products.PlonePAS.utils import scale_image
    from Products.CMFCore.utils import _checkPermission
    from AccessControl import Unauthorized
    from Products.CMFCore.permissions import ManageUsers


    if getattr(MembershipTool, '__inigo_memberportrait_patched', False):
        return

    def changeMemberPortrait(self, portrait, id=None):
        """update the portait of a member.

        Modified from CMFPlone version to URL-quote the member id.
        """
        safe_id = self._getSafeMemberId(id)
        authenticated_id = self.getAuthenticatedMember().getId()
        safe_authenticated_id = self._getSafeMemberId(authenticated_id)
        if not safe_id:
            safe_id = safe_authenticated_id
        if safe_id != safe_authenticated_id and not _checkPermission(
                ManageUsers, self):
            raise Unauthorized
        if portrait and portrait.filename:
            scaled, mimetype = scale_image(portrait)
            portrait = Image(id=safe_id, file=scaled, title='')
            membertool = getToolByName(self, 'portal_memberdata')
            membertool._setPortrait(portrait, safe_id)

    def deletePersonalPortrait(self, id=None):
        """deletes the Portait of a member.

        Modified from CMFPlone version to URL-quote the member id.
        """
        safe_id = self._getSafeMemberId(id)
        authenticated_id = self.getAuthenticatedMember().getId()
        safe_authenticated_id = self._getSafeMemberId(authenticated_id)
        if not safe_id:
            safe_id = safe_authenticated_id
        if safe_id != safe_authenticated_id and not _checkPermission(
                ManageUsers, self):
            raise Unauthorized

        membertool = getToolByName(self, 'portal_memberdata')
        return membertool._deletePortrait(safe_id)

    MembershipTool.changeMemberPortrait = changeMemberPortrait
    MembershipTool.deletePersonalPortrait = deletePersonalPortrait
    MembershipTool.__inigo_memberportrait_patched = True


def _apply_comment_src_patch():
    if getattr(padcomment, '__inigo_comment_patched', False):
        return
    padcomment.notify_user = notify_user
    padcomment.__inigo_comment_patched = True
    

from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from plone.app.discussion.interfaces import IDiscussionSettings
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_base, Implicit
from zope.i18n import translate
from zope.i18nmessageid import Message
from Products.CMFPlone.utils import safe_unicode
from smtplib import SMTPException
from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.app.discussion import comment as padcomment
MAIL_NOTIFICATION_MESSAGE = u"""
${name} posted a comment on '${title}' (${link})

---
${text}
---

"""

def notify_user(obj, event):
    # Check if user notification is enabled
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)
    if not settings.user_notification_enabled:
        return

    # Get informations that are necessary to send an email
    mail_host = getToolByName(obj, 'MailHost')
    portal_url = getToolByName(obj, 'portal_url')
    portal = portal_url.getPortalObject()


    # Compose and send emails to all users that have add a comment to this
    # conversation and enabled user_notification.
    conversation = aq_parent(obj)
    content_object = aq_parent(conversation)

    sender = '"KSP Comment Notification" <no-reply@ilo.org>'

    # Check if a sender address is available
    if not sender:
        return

    # Avoid sending multiple notification emails to the same person
    # when he has commented multiple times.
    emails = set()
    for comment in conversation.getComments():
        if (obj != comment and
            comment.user_notification and comment.author_email):
            emails.add(comment.author_email)

    if obj.author_email and obj.author_email in emails:
        emails.remove(obj.author_email)

    if not emails:
        return

    subject = translate(_(u"A comment has been posted."),
                        context=obj.REQUEST)
    message = translate(Message(
            MAIL_NOTIFICATION_MESSAGE,
            mapping={'title': safe_unicode(content_object.title),
                     'link': content_object.absolute_url() +
                             '/view#' + obj.id,
                     'name': obj.author_name,
                     'text': obj.text}),
            context=obj.REQUEST)
    for email in emails:
        # Send email
        try:
            mail_host.send(message,
                           email,
                           sender,
                           subject,
                           charset='utf-8')
        except SMTPException:
            padcomment.logger.error('SMTP exception while trying to send an ' +
                         'email from %s to %s',
                         sender,
                         email)


def _apply_collectivesolr_facetednav_compat():
    try:
        from eea.faceted.vocabularies import portal
    except ImportError:
        return

    if getattr(portal.PortalVocabulariesVocabulary, '__inigo_solrcompat_patched', False):
        return

    from Products.CMFCore.utils import getToolByName
    from zope.component import getUtilitiesFor
    from eea.faceted.vocabularies.utils import IVocabularyFactory
    from zope.schema.vocabulary import SimpleVocabulary
    from zope.schema.vocabulary import SimpleTerm
    import operator
    from eea.faceted.vocabularies.utils import compare
    from eea.facetednavigation.widgets.text.widget import Widget as TextWidget
    from collective.solr.flare import PloneFlare
    from zope.component.hooks import getSite

    def __call__(self, context):
        """ See IVocabularyFactory interface
        """
        res = []
        vtool = getToolByName(context, 'portal_vocabularies', None)
        if vtool:
            vocabularies = vtool.objectValues()
            res.extend([(term.getId(), term.title_or_id())
                        for term in vocabularies])
        atvocabulary_ids = [elem[0] for elem in res]

        factories = getUtilitiesFor(IVocabularyFactory)
        res.extend([(factory[0], factory[0]) for factory in factories
                    if factory[0] not in atvocabulary_ids])

        res.sort(key=operator.itemgetter(1), cmp=compare)
        if ('', '') not in res:
            res.insert(0, ('', ''))
        items = [SimpleTerm(key, key, value) for key, value in res]
        return SimpleVocabulary(items)

    def query(self, form):
        result = self.__orig_query(form)
        if result.has_key('SearchableText'):
            stext = result['SearchableText'].get('query', '')
            if isinstance(stext, list):
                stext = ' '.join(set(stext))
            result['SearchableText'] = stext

        return result

    def getRID(self):
        site = getSite()
        brains = site.portal_catalog({'path':self['path_string']})
        return brains[0].getRID()

    TextWidget.__orig_query = TextWidget.query
    TextWidget.query = query
    PloneFlare.getRID = getRID
    portal.PortalVocabulariesVocabulary.__call__ = __call__
    portal.PortalVocabulariesVocabulary.__inigo_solrcompat_patched = True

def _apply_xmppcore_lowercase_postNode():
    try:
        from jarn.xmpp.core.browser.pubsub import PubSubFeedMixIn
    except:
        return

    if getattr(PubSubFeedMixIn, '__inigo_xmppcore_lowercase_postNode', False):
        return

    __orig_postNode = PubSubFeedMixIn.postNode
    def postNode(self):
        result = __orig_postNode(self)
        return result.lower() if result else result

    PubSubFeedMixIn.postNode = postNode
    PubSubFeedMixIn.__inigo_xmppcore_lowercase_postNode = True


def _apply_eea_empty_folder_hack():
    try:
        from eea.facetednavigation.browser.app.query import FacetedQueryHandler
    except:
        return

    if getattr(FacetedQueryHandler, '__inigo_faceted_empty_hack', False):
        return

    __orig_query = FacetedQueryHandler.query
    def query(self, *args, **kwargs):
        result = __orig_query(self, *args, **kwargs)
        if not result:
            # hack to empty query
            self.request.contentFilter = [
                ('portal_type', 'ilo.customization.dummy')
            ]
        return result

    FacetedQueryHandler.query = query
    FacetedQueryHandler.__inigo_faceted_empty_hack = True


def _apply_remove_integer_grouping():
    from zope.i18n.format import NumberFormat

    if getattr(NumberFormat, '__inigo_force_symbolgroup_patched', False):
        return

    _orig_init = NumberFormat.__init__
    def __init__(self, pattern=None, symbols={}):
        symbols['group'] = ''
        return _orig_init(self, pattern, symbols)

    NumberFormat.__init__ = __init__
    NumberFormat.__inigo_force_symbolgroup_patched = True


def _apply_wrap_broken_blobgetfilename():
    from collective.contentleadimage.extender import LeadimageBlobImageField

    if getattr(LeadimageBlobImageField, '__inigo_blobgetfilename_patched', False):
        return

    class wrapper(object):
    
        def __init__(self, context):
            self.context = context
    
        def getFilename(self):
            return ''
    
        def __getattr__(self, key):
            if key in self.__dict__:
               return self.__dict__[key]
    
            if hasattr(self.context, key):
               return getattr(self.context, key)
    
            raise AttributeError
    
        def __setattr__(self, key, value):
            if key == 'context':
               self.__dict__[key] = value
    
            setattr(self.context, key, value)
    
    _orig_getUnwrapped = LeadimageBlobImageField.getUnwrapped
    def getUnwrapped(self, instance, **kwargs):
        result = _orig_getUnwrapped(self, instance, **kwargs)
        if result is not None and not hasattr(result, 'getFilename'):
            return wrapper(result)
        return result

    LeadimageBlobImageField.getUnwrapped = getUnwrapped
    LeadimageBlobImageField.__inigo_blobgetfilename_patched = True

def _patch_solgema_data_extender():
    try:
        from Solgema.fullcalendar.browser import adapters
    except ImportError, e:
        return

    if getattr(adapters, '__ploneun_dataextender_patched', False):
        return

    logger.info('Patching Solgema.fullcalendar with data extender support')

    from zope.component.hooks import getSite
    from ilo.customizations.interfaces import ICalendarDataExtender
    from zope.component import getAdapter

    _orig_dict_from_events = adapters.dict_from_events

    def dict_from_events(events, editable=None, state=None, color=None, css=None):
        result = _orig_dict_from_events(events, editable, state, color, css)
        site = getSite()
        newresult = []
        for item in result:
            uid = item['id'].replace('UID_','')
            brains = site.portal_catalog(UID=uid)
            brain = None
            if brains:
                brain = brains[0]

            portal_type = brain.portal_type if brain else None
            extender = getAdapter(site, ICalendarDataExtender, name=portal_type)
            item.update(extender(brain))
            newresult.append(item)
        return newresult
    
    adapters.dict_from_events = dict_from_events
    adapters.__ploneun_dataextender_patched = True
