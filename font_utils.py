import os
import otf2ttf as o2t
import ttc2ttf as c2f
import matplotlib.font_manager as FM
from PIL.ImageFont import FreeTypeFont


def get_font_list(ext_list):
    fonts = {}
    font_files = FM.list_fonts(FM.win32FontDirectory(), ext_list)

    for f in font_files:
        for i in range(10):
            try:
                font = FreeTypeFont(font=f, index=i)
            except IOError:
                break
            direc, sep, file_name = f.rpartition(os.sep)

            family, style = font.getname()
            fonts.setdefault("{:40s}{}".format(family, style), (family, style, file_name, i))
    return fonts


def otf2ttf(font_file_name, out_direc):
    if font_file_name.lower().endswith(".otf"):
        out_path = '{}.ttf'.format(os.path.join(out_direc, os.path.splitext(font_file_name)[0]))
        o2t.main([os.path.join(FM.win32FontDirectory(), font_file_name), '--output', out_path])
        return out_path
    return ''


def ttc2ttf(font_file_name, face_index, out_direc):
    if font_file_name.lower().endswith(".ttc"):
        return c2f.create_ttf_from_ttc(font_file_name, face_index, out_direc)
    return ''
