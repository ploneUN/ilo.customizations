import MembershipTool
from Products.CMFCore import utils
from ilo.customizations.config import PROJECTNAME
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl import AuthEncoding
import patches


GLOBALS = globals()
registerDirectory('skins', GLOBALS)

tools = (MembershipTool.MembershipTool,)

patches.apply_patches()


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    
    utils.ToolInit(PROJECTNAME + ' Tool',
             tools=tools,
             product_name=PROJECTNAME,
             icon="tool.gif",
             ).initialize(context)


