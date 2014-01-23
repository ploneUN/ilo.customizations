from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore import utils
from Products.PlonePAS.tools.membership import MembershipTool as BaseTool
from Products.CMFCore.permissions import ManageUsers

class MembershipTool( BaseTool ):
    """ Replace the membership tool in order to change the process of
        creating the member folder
    """

    meta_type='ilo Membership Tool'
    security = ClassSecurityInfo()
    plone_tool = 1

    security.declareProtected(ManageUsers, 'getMemberById')
    def getMemberById(self, id):
        # case insensitive
        for memberid in self.listMemberIds():
            if id.lower() == memberid.lower():
                id = memberid
                break
        return super(MembershipTool, self).getMemberById(id)

    security.declarePublic('getPersonalPortrait')
    def getPersonalPortrait(self, id=None, verifyPermission=0):
        # case insensitive
        for memberid in self.listMemberIds():
            if id.lower() == memberid.lower():
                id = memberid
                break
        return super(MembershipTool, self).getPersonalPortrait(id, verifyPermission)

    security.declarePublic('getMemberInfo')
    def getMemberInfo(self, memberId=None):
        """
        Return 'harmless' Memberinfo of any member, such as Full name,
        Location, etc
        """
        if not memberId:
            member = self.getAuthenticatedMember()
        else:
            member = self.getMemberById(memberId)

        if member is None:
            return None

        memberinfo = { 'fullname'    : member.getProperty('fullname'),
                       'description' : member.getProperty('description'),
                       'location'    : member.getProperty('location'),
                       'language'    : member.getProperty('language'),
                       'home_page'   : member.getProperty('home_page'),
                       'username'    : member.getUserName(),
                       'office'      : member.getProperty('office'),
                       'themes'      : member.getProperty('themes'),
                       'email'       : member.getProperty('email'),
                       'jobtitle'    : member.getProperty('jobtitle'),
                       'skypeid'     : member.getProperty('skypeid'),
                       'conduct'     : member.getProperty('conduct')
                     }

        return memberinfo

InitializeClass(MembershipTool)
