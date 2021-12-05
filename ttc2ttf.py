# Authors of this file's function are yhchen & Hiroyuki Tsutsumi [https://github.com/yhchen/ttc2ttf]
import os
import matplotlib.font_manager as FM
from struct import pack_into, unpack_from


def ceil4(n):
    # returns the next integer which is a multiple of 4
    return (n + 3) & ~3


def create_ttf_from_ttc(font_file_name, face_index, out_direc):
    filename = '{}{}{}'.format(FM.win32FontDirectory(), os.sep, font_file_name)
    in_file = open(filename, "rb")
    buf = in_file.read()
    in_file.close()

    if filename.lower().endswith(".ttc"):
        filename = filename[:-4]

    if buf[:4] != b"ttcf":
        out_filename = "%s.ttf" % filename
        out_file = open(out_filename, "wb")
        out_file.write(buf)
        #  end, so we don’t have to close the files or call exit() here
    else:
        ttf_count = unpack_from("!L", buf, 0x08)[0]
        ttf_offset_array = unpack_from("!"+ttf_count*"L", buf, 0x0C)
        table_header_offset = ttf_offset_array[face_index]
        table_count = unpack_from("!H", buf, table_header_offset+0x04)[0]
        header_length = 0x0C + table_count * 0x10

        table_length = 0
        for j in range(table_count):
            length = unpack_from("!L", buf, table_header_offset+0x0C+0x0C+j*0x10)[0]
            table_length += ceil4(length)

        total_length = header_length + table_length
        new_buf = bytearray(total_length)
        header = unpack_from(header_length*"c", buf, table_header_offset)
        pack_into(header_length*"c", new_buf, 0, *header)
        current_offset = header_length

        for j in range(table_count):
            offset = unpack_from("!L", buf, table_header_offset+0x0C+0x08+j*0x10)[0]
            length = unpack_from("!L", buf, table_header_offset+0x0C+0x0C+j*0x10)[0]
            pack_into("!L", new_buf, 0x0C+0x08+j*0x10, current_offset)
            current_table = unpack_from(length*"c", buf, offset)
            pack_into(length*"c", new_buf, current_offset, *current_table)
            current_offset += ceil4(length)

        out_file_path = "%s%s%s%d.ttf" % (out_direc, os.sep, font_file_name[:-4], face_index)
        out_file = open(out_file_path, "wb")
        out_file.write(new_buf)
        return out_file_path
