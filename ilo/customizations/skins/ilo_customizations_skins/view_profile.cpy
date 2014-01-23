## Controller Python Script "personalize"
##bind container=container
##bind context=context

member=context.portal_membership.getAuthenticatedMember()

portal_url = context.portal_url.getPortalObject().absolute_url()
context.REQUEST.RESPONSE.redirect('%s/author/%s' % (portal_url, member.getId()))
