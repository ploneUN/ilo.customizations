from Products.Five import zcml
from Products.Five import fiveconfigure
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_ilo_customizations():
    """
    The @onsetup decorator causes the execution of this body to be deferred until the setup of the Pone site testing layer.
    """

    # Load the ZCML configuration for the ilo.customizations package
    fiveconfigure.debug_mode = True
    import ilo.customizations
    zcml.load_config('configure.zcml',ilo.customizations)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products should
    # be available. This can't happen untuk after we have loaded the ZCML

    ztc.installPackage('ilo.customizations')

# The order here is important: we first call the (deferred) function which
# installs the products we need for the ilo package. Then, we let
# PloneTestCase set up this product on installation.

setup_ilo_customizations()
ptc.setupPloneSite(products=['ilo.customizations'])

class EnrapTestCase(ptc.PloneTestCase):
    """ We use this base class for all the tests in this package. If necessary, we can put common utility or setup code here.
    """
