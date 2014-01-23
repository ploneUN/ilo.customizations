from zope.component import queryUtility
from Acquisition import aq_parent, aq_base, Implicit
from Products.CMFPlone.utils import safe_unicode
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate
from zope.i18nmessageid import Message
from plone.app.discussion import PloneAppDiscussionMessageFactory as _
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.discussion.comment import logger
from smtplib import SMTPException

MAIL_NOTIFICATION_MESSAGE = u"""
${name} posted a comment on '${title}' (${link})

---
${text}
---

"""


def notify_owner(obj, event):
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IDiscussionSettings, check=False)

    # Get informations that are necessary to send an email
    mail_host = getToolByName(obj, 'MailHost')
    portal_url = getToolByName(obj, 'portal_url')
    portal = portal_url.getPortalObject()
    mtool = getToolByName(obj, 'portal_membership')
    sender = '"KSP Comment Notification" <no-reply@ilo.org>'

    # Check if a sender address is available
    if not sender:
        return


    conversation = aq_parent(obj)
    content_object = aq_parent(conversation)
    
    creator = content_object.Creator()
    member = mtool.getMemberById(creator)
    mto = member.getProperty('email', '')

    if not mto:
        return

    # Compose email
    subject = translate(_(u"A comment has been posted."), context=obj.REQUEST)
    message = translate(Message(MAIL_NOTIFICATION_MESSAGE,
        mapping={
            'title': safe_unicode(content_object.title),
            'link': content_object.absolute_url() + '/view#' + obj.id,
            'text': obj.text,
            'name': obj.author_name
            }),
        context=obj.REQUEST)

    # Send email
    try:
        mail_host.send(message, mto, sender, subject, charset='utf-8')
    except SMTPException, e:
        logger.error('SMTP exception (%s) while trying to send an ' +
                     'email notification to the comment moderator ' +
                     '(from %s to %s, message: %s)',
                     e,
                     sender,
                     mto,
                     message)

