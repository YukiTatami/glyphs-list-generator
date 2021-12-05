import os
import threading
import font_utils
from enum import Enum
from tkinter import *
from tkinter import ttk
from tkinter.font import Font
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, portrait
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
import fontTools.ttLib as ttlib


class GlyphDispStyle(Enum):
    CID = 0
    UNICODE = 1


def set_info(out_direc, filename):
    # 保存先
    pdf_canvas = canvas.Canvas("{0}/{1}.pdf".format(out_direc, filename), pagesize=portrait(A4))
    pdf_canvas.setTitle("")  # 表題
    pdf_canvas.setSubject("")  # 件名
    return pdf_canvas


A4_SIZE_X = 210  # mm
A4_SIZE_Y = 297  # mm
PAD_X = 10  # mm
PAD_Y = 10  # mm
# 基本多言語面
CODE_POINT_BMP = 65535
# 追加多言語面
CODE_POINT_SMP = 131071
# 追加漢字面
CODE_POINT_SIP = 196607
# 第3漢字面
CODE_POINT_TIP = 262143
# Adobe-japan1のCIDの収容範囲
ADOBE_JP1_0 = 8283
ADOBE_JP1_1 = 8358
ADOBE_JP1_2 = 8719
ADOBE_JP1_3 = 9353
ADOBE_JP1_4 = 15443
ADOBE_JP1_5 = 20316
ADOBE_JP1_6 = 23057
ADOBE_JP1_7 = 23059

class GlyphsListPage:
    @staticmethod
    def GetNeedDataShape():
        return (0, 0)

    @classmethod
    def IsValidDataShape(cls, data):
        row, column = cls.GetNeedDataShape()
        return len(data) <= row and len(data[0]) == column

    @classmethod
    def AddPage(cls, pdf_canvas, data, font_id):
        return


class UnicodeGlyphsListPage(GlyphsListPage):
    @staticmethod
    def GetNeedDataShape():
        glyph_num_in_column = 16
        row_height = (A4_SIZE_X - PAD_X * 2) / (glyph_num_in_column + 1)  # 見出し分余分にとる
        row_in_page = int((A4_SIZE_Y - PAD_Y * 2) / row_height)
        return (row_in_page, glyph_num_in_column)

    @classmethod
    def AddPage(cls, pdf_canvas, data, code_point_offset, font_id):
        if not cls.IsValidDataShape(data):
            return
        _, origin_column = cls.GetNeedDataShape()

        # 見出し（行）の追加
        data.insert(0, [format(i, 'X') for i in range(origin_column)])
        # 見出し（列）の追加
        for i, r in enumerate(data):
            r.insert(0, 'U+' if i == 0 else format(code_point_offset + (i - 1) * origin_column, '05X'))
        row = len(data)
        culumn = len(data[0])

        col_width = row_height = (A4_SIZE_X - PAD_X * 2) / (origin_column + 1)  # 見出し分余分にとる
        table = Table(data, colWidths=col_width*mm, rowHeights=row_height*mm)

        GLYPH_FONT_SIZE = 18
        HEADING_C_FONT_SIZE = 9   # 見出し（列）のフォントサイズ

        # tableの装飾
        table.setStyle(TableStyle(
            [
                ('FONT'     , (1, 1), (-1, -1), font_id, GLYPH_FONT_SIZE),
                ('ALIGN'    , (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN'   , (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX'      , (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.gray),
                # 見出し（行）
                ('TEXTCOLOR' , (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                # 見出し（列）
                ('FONTSIZE'  , (0, 1), (0, -1), HEADING_C_FONT_SIZE),
                ('BACKGROUND', (0, 1), (0, -1), (0.9, 0.9, 0.9)),
            ]))

        # table位置（左下原点）
        x = (A4_SIZE_X - col_width * culumn - PAD_X * 2) / 2 + PAD_X
        y = A4_SIZE_Y - (PAD_Y + row_height * row)
        table.wrapOn(pdf_canvas, x*mm, y*mm)  
        table.drawOn(pdf_canvas, x*mm, y*mm)
        pdf_canvas.showPage()

# 面倒なのでUnicodeのをコピペ
class CidGlyphsListPage(GlyphsListPage):
    @staticmethod
    def GetNeedDataShape():
        glyph_num_in_column = 20
        row_height = (A4_SIZE_X - PAD_X * 2) / (glyph_num_in_column + 1)  # 見出し分余分にとる
        row_in_page = int((A4_SIZE_Y - PAD_Y * 2) / row_height)
        return (row_in_page, glyph_num_in_column)

    @classmethod
    def AddPage(cls, pdf_canvas, data, gid_offset, font_id):
        if not cls.IsValidDataShape(data):
            return
        _, origin_column = cls.GetNeedDataShape()

        # 見出し（行）の追加
        data.insert(0, [i for i in range(origin_column)])
        # 見出し（列）の追加
        for i, r in enumerate(data):
            r.insert(0, 'CID' if i == 0 else format(gid_offset + (i - 1) * origin_column, '04'))
        row = len(data)
        culumn = len(data[0])

        col_width = row_height = (A4_SIZE_X - PAD_X * 2) / (origin_column + 1)  # 見出し分余分にとる
        table = Table(data, colWidths=col_width*mm, rowHeights=row_height*mm)

        GLYPH_FONT_SIZE = 16
        HEADING_C_FONT_SIZE = 7   # 見出し（列）のフォントサイズ

        # tableの装飾
        table.setStyle(TableStyle(
            [
                ('FONT'     , (1, 1), (-1, -1), font_id, GLYPH_FONT_SIZE),
                ('ALIGN'    , (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN'   , (0, 0), (-1, -1), 'MIDDLE'),
                ('BOX'      , (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.gray),
                # 見出し（行）
                ('TEXTCOLOR' , (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, 0), (-1, 0), colors.black),
                # 見出し（列）
                ('FONTSIZE'  , (0, 1), (0, -1), HEADING_C_FONT_SIZE),
                ('BACKGROUND', (0, 1), (0, -1), (0.9, 0.9, 0.9)),
            ]))

        # table位置（左下原点）
        x = (A4_SIZE_X - col_width * culumn - PAD_X * 2) / 2 + PAD_X
        y = A4_SIZE_Y - (PAD_Y + row_height * row)
        table.wrapOn(pdf_canvas, x*mm, y*mm)  
        table.drawOn(pdf_canvas, x*mm, y*mm)
        pdf_canvas.showPage()


def add_unicode_glyphs_list(pdf_canvas, font_id, code_point_list):
    code_point_list = sorted(code_point_list)
    tmp_data = []
    for code_point in code_point_list:
        # 空詰め
        for _ in range(len(tmp_data), code_point):
            tmp_data.append('')
        tmp_data.append(chr(code_point))

    p_row, p_column = UnicodeGlyphsListPage.GetNeedDataShape()
    row = -(-len(tmp_data) // p_column)  # 総行数（切り上げ）
    # グリフの二次元配列
    data = []
    for r in range(row):
        # chr(i)では空文字が返されてしまう（CiD）と同じようにリストとってきて""を入れるようにする
        data.append([tmp_data[i] if i < len(tmp_data) else '' for i in range(r * p_column, (r + 1) * p_column)])

    # 1ページ毎に描画
    for head in range(0, row, p_row - 1):
        UnicodeGlyphsListPage.AddPage(pdf_canvas, data[head:min(head + p_row - 1, row)], head * p_column, font_id)


def add_cid_glyphs_list(pdf_canvas, font_id, code_id_dic):
    code_id_list = sorted(code_id_dic.items())
    tmp_data = []
    for glyph_id, code in code_id_list:
        # 空詰め
        for _ in range(len(tmp_data), glyph_id):
            tmp_data.append('')
        tmp_data.append(chr(code))

    p_row, p_column = CidGlyphsListPage.GetNeedDataShape()
    row = -(-len(tmp_data) // p_column)  # 総行数（切り上げ）
    # グリフの二次元配列
    data = []
    for r in range(row):
        data.append([tmp_data[i] if i < len(tmp_data) else '' for i in range(r * p_column, (r + 1) * p_column)])

    # 1ページ毎に描画
    for head in range(0, row, p_row - 1):
        CidGlyphsListPage.AddPage(pdf_canvas, data[head:min(head + p_row - 1, row)], head * p_column, font_id)

def print_pages(pdf_canvas, out_direc, font_file_name, face_index, glyph_style):
    tgt_font_name = font_file_name
    has_tmp_font_file = False  # 一次的にフォントファイルを生成して処理が完了したら削除する

    # .ttcファイルは.ttfファイルに分割してから処理
    if font_file_name.lower().endswith(".ttc"):
        tgt_font_name = font_utils.ttc2ttf(font_file_name, face_index, out_direc)
        has_tmp_font_file = True
    # .otfファイルは.ttfファイルに変換してから処理
    elif font_file_name.lower().endswith(".otf"):
        tgt_font_name = font_utils.otf2ttf(font_file_name, out_direc)
        has_tmp_font_file = True

    # フォントの読み込み(識別フォント名は同名が許されないのでフォントファイル名をそのまま識別フォント名とする)
    ttf = TTFont(tgt_font_name, tgt_font_name)
    pdfmetrics.registerFont(ttf)

    # platformID
    WINDOWS = 3
    # encogingID(Windows)
    WIN_UNI_BMP = 1
    WIN_UNI_FULL_REPERTOIRE = 10
    # フォントファイルのディレクトリ(Windows)
    FONT_FOLDER = 'C:\Windows\Fonts'

    lib_ttf = ttlib.TTFont(os.path.join(FONT_FOLDER, tgt_font_name))
    cmap_table = None
    cmap_table = next(filter(lambda t:t.platformID == WINDOWS and t.platEncID == WIN_UNI_FULL_REPERTOIRE, lib_ttf['cmap'].tables), None)
    if cmap_table == None:
        cmap_table = next(filter(lambda t:t.platformID == WINDOWS and t.platEncID == WIN_UNI_BMP, lib_ttf['cmap'].tables), None)
    if cmap_table == None:
        return

    # CID順の表
    if glyph_style ==  GlyphDispStyle.CID:
        code_id_dic = {}
        for code, name in cmap_table.cmap.items():
            code_id_dic[lib_ttf.getGlyphID(name)] = code
        add_cid_glyphs_list(pdf_canvas, tgt_font_name, code_id_dic)
    # Unicode順の表
    elif glyph_style ==  GlyphDispStyle.UNICODE:
        code_point_list = []
        for code, _ in cmap_table.cmap.items():
            code_point_list.append(code)
        # max_code_point = next(reversed(cmap_table.cmap.keys()), None)
        add_unicode_glyphs_list(pdf_canvas, tgt_font_name, code_point_list)

    if has_tmp_font_file:
        os.remove(tgt_font_name)


def generate_pdf(out_direc, out_file_name, font_file_name, face_index, glyph_style):
    pdf_canvas = set_info(out_direc, out_file_name)
    print_pages(pdf_canvas, out_direc, font_file_name, face_index, glyph_style)
    pdf_canvas.save()


class GlyphsListGenerator(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.fonts = font_utils.get_font_list(['ttf', 'ttc', 'otf'])
        self.create_widgets()
        self.pack()

    def create_widgets(self):
        WIDGET_FONT_SIZE = 12
        f = Font("", size=WIDGET_FONT_SIZE)
        super().option_add("*TCombobox*Listbox.Font", f)

        # フォントを選択するコンボボックス
        self.combo = ttk.Combobox(self, values=list(self.fonts.keys()), width='60', font=("", WIDGET_FONT_SIZE), state='readonly')
        self.combo.pack(pady=5)

        # ラジオボタン（表示形式を指定）
        self.radio_var = IntVar()
        radio_0 = Radiobutton(self, value=0, variable=self.radio_var, text='CID/GID')
        radio_1 = Radiobutton(self, value=1, variable=self.radio_var, text='Unicode')
        radio_0.pack()
        radio_1.pack()
        self.radio_var.set(0)

        # 説明用ラベル
        entry_frame = ttk.Frame(self)
        entry_frame.pack(pady=5)
        label_cid_desc = ttk.Label( self,
                                    text="[CID(Adobe-Japan1)] 0-{} 1-{} 2-{} 3-{} 4-{} 5-{} 6-{} 7-{}".format(
                                        ADOBE_JP1_0, ADOBE_JP1_1, ADOBE_JP1_2, ADOBE_JP1_3, ADOBE_JP1_4, ADOBE_JP1_5, ADOBE_JP1_6, ADOBE_JP1_7),
                                    font=("", WIDGET_FONT_SIZE))
        label_cid_desc.pack()
        label_code_point_desc = ttk.Label(self,
                                          text="[code point] BMP-{} SMP-{} SIP-{} TIP-{}".format(CODE_POINT_BMP, CODE_POINT_SMP, CODE_POINT_SIP, CODE_POINT_TIP),
                                          font=("", WIDGET_FONT_SIZE))
        label_code_point_desc.pack()

        # 実行ボタン
        self.button = ttk.Button(self, text="Generate PDF", command=self.execute_gen_pdf)
        self.button.pack(pady=5)

        # ステータスバー
        self.status = ttk.Label(self, text='Select target font.', font=("", WIDGET_FONT_SIZE), relief=SUNKEN, anchor=SW)
        self.status.pack(fill=X)


    def execute_gen_pdf(self):
        if(self.combo.get() == ''):
            return
        self.button["state"] = "disable"
        self.status["text"] = 'Generating...'
        self.status["background"] = '#DDDD77'
        t = threading.Thread(target=self.execute_gen_pdf_impl)
        t.start()


    def execute_gen_pdf_impl(self):
        if(self.combo.get() == ''):
            return
        family, style, file_name, face_index = self.fonts[self.combo.get()]
        out_direc = os.getcwd()
        out_file_name = 'glyphs_list_{}_{}_{}'.format(family, style, 'cid' if self.radio_var.get() == 0 else 'unicode')
        generate_pdf(out_direc, out_file_name, file_name, face_index, GlyphDispStyle(self.radio_var.get()))

        gen_path = "{}{}{}.pdf".format(out_direc, os.sep, out_file_name)
        self.status["text"] = 'Generated PATH={}'.format(gen_path)
        self.status["background"] = '#77FFAA'
        os.startfile(gen_path)
        self.button["state"] = "normal"


if __name__ == '__main__':
    window = Tk()
    window.title("Glyphs List Generator")
    GlyphsListGenerator(window)
    window.mainloop()
