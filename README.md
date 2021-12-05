# glyphs-list-generator

A tool to generate a pdf glyph table from a font file(.otf, .ttf, .ttc). 
It supports displaying glyphs not only in Unicode order but also in CID/GID order. 
Character search is available.

[Usage]
Double-click on glyphs_list_generator.exe to execute it.
Select any installed font (under C:\Windows\Fonts) from the pull-down menu at the top of the displayed GUI.
Then, use the radio buttons to select either [CID/GID] or [Unicode] as the display format.
Finally, click the [Generate PDF] button at the bottom of the GUI to generate a PDF of the glyph list, which will be extracted as soon as the process is complete.
The output destination of the PDF is shown in the status bar at the bottom of the GUI (in the same directory as the exe).

The .spec file is used to convert a python file into an exe file with PyInstaller.

************************
フォントファイル(.otf, .ttf, .ttc)からpdfのグリフ一覧を生成するツールです。
Unicode順だけでなく、CID/GID順でのグリフ表示にも対応しています。
文字検索も可能です。

[使い方]
glyphs_list_generator.exeに対しダブルクリックで実行を行ってください。
表示されたGUI上部のプルダウンで任意のインストールされているフォント（C:\Windows\Fonts以下）を選択します。
その後、表示形式として[CID/GID]と[Unicode]のどちらかをラジオボタンで選択します。
最後にGUI下部の[Generate PDF]ボタンをクリックするとグリフ一覧のPDFが生成され、処理が終了し次第展開されます。
PDFの出力先はGUI最下部のステータスバーに記載されます（exeと同ディレクトリ）。

.specファイルはpythonファイルをPyInstallerでexeファイル化する際に用います。
