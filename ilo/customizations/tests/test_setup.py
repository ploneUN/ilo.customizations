import unittest

from ilo.customizations.tests.base import EnrapTestCase

class TestSetup(EnrapTestCase):

    def test_portal_title(self):
        self.assertEquals("ENRAP", self.portal.getProperty('title'))

    def test_portal_description(self):
        self.assertEquals("Welcome to ENRAP",self.portal.getProperty('description'))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
