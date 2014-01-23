from five import grok
from ilo.customizations.interfaces import ICalendarDataExtender
from zope.interface import Interface

class DefaultCalendarDataExtender(grok.Adapter):
    grok.context(Interface)
    grok.implements(ICalendarDataExtender)

    def __init__(self, context):
        self.context = context

    def __call__(self, brain):
        return {
            'footnote': ''
        }

class ILOEventCalendarDataExtender(grok.Adapter):
    grok.context(Interface)
    grok.implements(ICalendarDataExtender)
    grok.name('ILOEvent')

    def __init__(self, context):
        self.context = context

    def __call__(self, brain):
        return {
            'footnote': brain.getObject().location or ''
        }


class MissionCalendarDataExtender(grok.Adapter):
    grok.context(Interface)
    grok.implements(ICalendarDataExtender)
    grok.name('Mission')

    def __init__(self, context):
        self.context = context

    def __call__(self, brain):
        return {
            'footnote': brain.getObject().mission_event_location or ''
        }

