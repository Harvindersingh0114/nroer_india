import json
import pkgutil
from collections import namedtuple
from gettext import gettext as _
from constants import content_formats

""" Content Kind Constants """

TOPIC = "topic"
VIDEO = "video"
AUDIO = "audio"
DOCUMENT = "document"
LICENSE = "CC BY-SA"

choices = (
    (TOPIC, _("Topic")),
    (VIDEO, _("Video")),
    (AUDIO, _("Audio")),
    (DOCUMENT, _("Document")),
)

""" File Format (extension) to Content Kind Mapping """
MAPPING = {
    content_formats.MP4: VIDEO,
    content_formats.MP3: AUDIO,
    content_formats.PDF: DOCUMENT,
}

class Kind(namedtuple("Kind", ["id", "name"])):
    pass

def generate_list(constantlist):
    for id, kind in constantlist.items():
        yield Kind(id=id, **kind)
