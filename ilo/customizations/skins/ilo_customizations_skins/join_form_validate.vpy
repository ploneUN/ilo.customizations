## Controller Python Script "validate_registration"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=username='',email='',password='',password_confirm='',fullname='',office='',themes='',conduct='',
##title=validates the Registration of a User

from Products.CMFPlone import PloneMessageFactory as _

reg_tool=context.portal_registration
def missing(field):
    state.setError(field, _(u'This field is required, please provide some information.'), 'input_required')
def nomatch(field):
    state.setError(field, _(u'Passwords do not match.'), 'nomatch_password')
def minlimit(field):
    state.setError(field, _(u'Passwords must contain at least 5 letters.'), 'min_password')
def notallowed(field):
    state.setError(field, _(u'This username is reserved. Please choose a different name.'), 'not_allowed')
def invalid(field):
    state.setError(field, _(u'Invalid input value.'), 'invalid_inputval')

portal = context.portal_url.getPortalObject()

if not username:
    missing('username')
if not email:
    missing('email')
if not fullname:
    missing('fullname')
if not office:
    missing('office')
if username and username == portal.getId():
    notallowed('username')

if  email.count('@ilo.org') != 1:
    state.setError('email', _(u'This email is not a valid ILO email address. Please enter a valid ILO email address'), 'not_allowed')

if not portal.validate_email:
     if password!=password_confirm:
         nomatch('password')
         nomatch('password_confirm')

     if not password:
         missing('password')
     if not password_confirm:
         missing('password_confirm')

     if not state.getError('password') and len(password) < 5:
         minlimit('password')
         minlimit('password_confirm')

if not state.getError('username') and not reg_tool.isMemberIdAllowed(username):
    state.setError('username',
                   _(u'The login name you selected is already in use or is not valid. Please choose another.'),
                   'username_invalid' )

if  conduct != "agree":
    state.setError('conduct', _(u'You need to agree to register.'), 'not_allowed')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state

