from plone.indexer.decorator import indexer
from Products.ILOIntranetTypes.interfaces import IMissionReport, IILOEvent
from Products.ATContentTypes.interfaces.file import IATFile
from Products.ATContentTypes.interfaces.interfaces import IATContentType
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFCore.utils import getToolByName

# iloevent, missionreport, file

TYPES={
    'document': [
        'application/msword',
        'application/vnd.ms-word',
        'application/vnd.wordperfect',
        'application/vnd.sun.xml.writer',
        'application/vnd.sun.xml.writer.global',
        'application/vnd.sun.xml.writer.template',
        'application/vnd.stardivision.writer',
        'application/vnd.oasis.opendocument.text',
        'application/vnd.oasis.opendocument.text-template',
        'application/vnd.oasis.opendocument.text-web',
        'application/vnd.oasis.opendocument.text-master',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.template',
    ],
    'spreadsheet': [
        'application/vnd.ms-excel',
        'application/vnd.stardivision.calc',
        'application/vnd.sun.xml.calc',
        'application/vnd.sun.xml.calc.template',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.template',
        'application/vnd.oasis.opendocument.spreadsheet',
        'application/vnd.oasis.opendocument.spreadsheet-template'
    ],
    'presentation': [
        'application/vnd.ms-powerpoint',
        'application/vnd.stardivision.impress',
        'application/vnd.sun.xml.impress',
        'application/vnd.sun.xml.impress.template',
        'application/vnd.oasis.opendocument.presentation',
        'application/vnd.oasis.opendocument.presentation-template',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.presentationml.template'
   ] 
}

def get_type_string(mimetype):
    for k, v in TYPES.items():
        if mimetype in v:
            return k
    return None

@indexer(IMissionReport)
def missionreport_file_type(obj, **kw):
    types = []
    schema = obj.Schema()
    for field in ['attachment1', 'attachment2', 'attachment3', 'attachment5']:
        contentType = schema[field].getContentType(obj)
        if not contentType:
            continue
        t = get_type_string(contentType)
        if t:
            types.append(t)
    return tuple(set(types))

@indexer(IILOEvent)
def iloevent_file_type(obj, **kw):
    types = []
    schema = obj.Schema()
    for field in ['attachment_attendees', 'attachment2', 'attachment3',
            'attachment4', 'attachment5']:
        contentType = schema[field].getContentType(obj)
        if not contentType:
            continue
        t = get_type_string(contentType)
        if t:
            types.append(t)
    return tuple(set(types))

@indexer(IATFile)
def atfile_file_type(obj, **kw):
    field = obj.Schema()['file']
    contentType = field.getContentType(obj)
    t = get_type_string(contentType)
    if t:
        return (t, )
    return ()


@indexer(IATContentType)
def atct_creator_fullname(obj, **kw):
    schema = obj.Schema()
    result = []
    mtool = getToolByName(obj, 'portal_membership')
    for creator in schema['creators'].get(obj) or []:
        member = mtool.getMemberById(creator)
        if not member:
            continue
        result.append(member.getProperty('fullname'))
    return ' '.join(result)


@indexer(IDexterityContent)
def dexterity_creator_fullname(obj, **kw):
    creators = getattr(obj, 'creators', []) or []
    mtool = getToolByName(obj, 'portal_membership')
    result = []
    for creator in creators:
        member = mtool.getMemberById(creator)
        if not member:
            continue
        result.append(member.getProperty('fullname'))
    return ' '.join(result)
