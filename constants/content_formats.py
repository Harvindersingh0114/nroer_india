import json
import pkgutil
from collections import namedtuple
from gettext import gettext as _

""" File Format Constants """

# constants for Video format
MP4 = "mp4"
MP4_MIMETYPE = "video/mp4"

# constants for Subtitle format
VTT = "vtt"
VTT_MIMETYPE = ".vtt"
SRT = "srt"
SRT_MIMETYPE = "text/srt"

# constants for Audio format
MP3 = "mp3"
MP3_MIMETYPE = ".mp3"

# constants for Document format
PDF = "pdf"
PDF_MIMETYPE = "application/pdf"

# constants for Thumbnail format
JPG = "jpg"
JPG_MIMETYPE = "image/jpeg"
JPEG = "jpeg"
PNG = "png"
PNG_MIMETYPE = "image/png"
GIF = "gif"
GIF_MIMETYPE = "image/gif"


JSON = "json"
JSON_MIMETYPE = "application/json"
SVG = "svg"
SVG_MIMETYPE = "image/svg"
GRAPHIE = "graphie"
GRAPHIE_MIMETYPE = ".graphie"


choices = (
    (MP4, _("MP4 Video")),

    (VTT, _("VTT Subtitle")),
    (SRT, _("SRT Subtitle")),

    (MP3, _("MP3 Audio")),

    (PDF, _("PDF Document")),

    (JPG, _("JPG Image")),
    (JPEG, _("JPEG Image")),
    (PNG, _("PNG Image")),
    (GIF, _("GIF Image")),
    (JSON, _("JSON")),
    (SVG, _("SVG Image")),
)

class Format(namedtuple("Format", ["id", "mimetype"])):
    pass

def generate_list(constantlist):
    for id, format in constantlist.items():
        yield Format(id=id, **format)


