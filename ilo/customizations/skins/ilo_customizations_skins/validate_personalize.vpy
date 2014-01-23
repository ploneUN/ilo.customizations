## Controller Python Script "validate_personalize"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=email='',fullname='',office='',conduct=''
##title=validates user preferences

from Products.CMFPlone import PloneMessageFactory as _

def missing(field):
    state.setError(field, _(u'This field is required, please provide some information.'), 'input_required')

if not email:
    missing('email')
if not fullname:
    missing('fullname')
if not office:
    missing('office')

if  conduct != "agree":
    state.setError('conduct', _(u'You need to agree.'), 'not_allowed')

if state.getErrors():
    context.plone_utils.addPortalMessage(_(u'Please correct the indicated errors.'), 'error')
    return state.set(status='failure')

return state
