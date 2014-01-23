from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

import ldap
from ZTUtils import make_query
from plone.protect import CheckAuthenticator
from zope.component import getUtility
from Products.CMFCore.interfaces import ISiteRoot
from Acquisition import aq_inner
from collective.xmpp.core.interfaces import IXMPPSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import re

class MemberUtil(BrowserView):
    def getMemberById(self, userid):
        mtool = getToolByName(self.context, 'portal_membership')
        return mtool.getMemberById(userid)

    def getMemberProperty(self, userid, prop):
        return self.getMemberById(userid).getProperty(prop)

    def _escapeNode(self, userid):
        patterns = [
            (r'\\',r'\\5c'),
            (r' ',r'\\20'),
            (r'"',r'\\22'),
            (r'&',r'\\26'),
            (r'\'',r'\\27'),
            (r'\/',r'\\2f'),
            (r':',r'\\3a'),
            (r'<',r'\\3c'),
            (r'>',r'\\3e'),
            (r'@',r'\\40')
        ]
        for p,s in patterns:
            userid = re.sub(p, s, userid)
        return userid

    def getMemberJID(self, userid):
        node = self._escapeNode(userid)
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IXMPPSettings, check=False)
        return node + '@' + settings.xmpp_domain        


class LDAPCompareView(BrowserView):

    def __call__(self):
        form = self.request.form
        submitted = form.get('form.submitted', False)
        self.ldapobj = ldap.initialize('ldap://ldap.bkk.ilo.vg:389')
        if submitted:   
            if form.get('form.button.Modify', None) is not None:
                self.manageUser(form.get('users', None), form.get('delete', []))

        return super(LDAPCompareView, self).__call__()

    def ldap_emails(self):
        r = self.ldapobj.search_s('o=ILO', 
                ldap.SCOPE_SUBTREE, '(objectClass=*)', ['mail'])
        result = []
        for dn, entry in r:
            result.append(entry['mail'][0].lower().strip())
        return result

    def email_exist(self, email):
        r = self.ldapobj.search_s('o=ILO', 
                ldap.SCOPE_SUBTREE, '(mail=%s)' % email,  ['mail'])
        return bool(len(list(r)))

    def plone_emails(self):
        mtool = self.context.portal_membership
        result = []
        for member in mtool.listMembers():
            result.append(member.getProperty('email').lower().strip())
        return result

    def expired_emails(self):
        ldapmails = self.ldap_emails()
        plonemails = self.plone_emails()

        result = []
        for e in plonemails:
            if e not in ldapmails:
                result.append(e)

        return result

    def expired_members(self):
        mtool = self.context.portal_membership
        members = mtool.listMembers()
        result = []

        for m in members:
            e = m.getProperty('email').lower().strip()
            if not self.email_exist(e):
                result.append(m)

        return result

    def makeQuery(self, **data):
        return make_query(**data)

    @property
    def searchResults(self):
        result = []
        for user in self.expired_members():
            info = {}
            info['id'] = user.getId()
            info['roles'] = []
            info['fullname'] = user.getProperty('fullname', '')
            info['email'] = user.getProperty('email', '')
            info['can_delete'] = user.canDelete()
            info['can_set_email'] = user.canWriteProperty('email')
            info['can_set_password'] = user.canPasswordSet()
            info['last_login_time'] = self.context.toLocalizedTime(
                    user.getProperty('last_login_time'))
            result.append(info)

        return result

    def manageUser(self, users=[], delete=[]):
        CheckAuthenticator(self.request)

        if delete:
            self.deleteMembers(delete)

    def deleteMembers(self, member_ids):
        # this method exists to bypass the 'Manage Users' permission check
        # in the CMF member tool's version
        context = aq_inner(self.context)
        mtool = getToolByName(self.context, 'portal_membership')

        # Delete members in acl_users.
        acl_users = context.acl_users
        if isinstance(member_ids, basestring):
            member_ids = (member_ids,)
        member_ids = list(member_ids)
        for member_id in member_ids[:]:
            member = mtool.getMemberById(member_id)
            if member is None:
                member_ids.remove(member_id)
            else:
                if not member.canDelete():
                    raise Forbidden
                if 'Manager' in member.getRoles() and not self.is_zope_manager:
                    raise Forbidden
        try:
            acl_users.userFolderDelUsers(member_ids)
        except (AttributeError, NotImplementedError):
            raise NotImplementedError('The underlying User Folder '
                                     'doesn\'t support deleting members.')

        # Delete member data in portal_memberdata.
        mdtool = getToolByName(context, 'portal_memberdata', None)
        if mdtool is not None:
            for member_id in member_ids:
                mdtool.deleteMemberData(member_id)

        # Delete members' local roles.
        mtool.deleteLocalRoles( getUtility(ISiteRoot), member_ids,
                               reindex=1, recursive=1 )

