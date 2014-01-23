from plone.app.upgrade.utils import loadMigrationProfile
from zope.component.hooks import getSite

def to1000(context, logger=None):
    loadMigrationProfile(context, 'profile-ilo.customizations:to1000')

def to1001(context, logger=None):
    loadMigrationProfile(context, 'profile-ilo.customizations:to1001')

def to1002(context, logger=None):
    loadMigrationProfile(context, 'profile-ilo.customizations:to1002')

def to1003(context, logger=None):
    loadMigrationProfile(context, 'profile-ilo.customizations:to1003')
    site = getSite()
    for userid in site.portal_membership.listMemberIds():
        member = site.portal_membership.getMemberById(userid)
        member.setMemberProperties({'ext_editor': True})
