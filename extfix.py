#!/usr/bin/env python3

# я очень люблю, когда всё по полочкам,
# прям люблю до обсессий. короче я
# рассортировал импорты в алфавитном порядке
import argparse
from pathlib import Path
import os
import logging

# и ещё я встречал такое, что импорты из внешних библиотек
# (не из стандартной библиотеки питона) пишут через пустую строку
# от системных
import magic as fm



log = logging.getLogger(__name__)

extsDict = {
    "image/png" : "png",
    "image/gif" : "gif",
    "image/jpeg" : "jpg",
    "text/html" : "html",
    "application/zip" : "zip",
    "application/vnd.rar" : "rar",
    "application/x-7z-compressed" : "7z"
}

extsBlacklist = [
    "inode/directory"
]

class BadFilenameException(Exception):
    pass

class NotInDictionaryException(Exception):
    pass

class ArgumentException(Exception):
    pass

FILENAME_PROHIBITED = ('<', '>', ':', '"', '\\', '|', '?', '*')

def get_ext(file):
    f = file.parts[-1]
    if any(i in f for i in FILENAME_PROHIBITED):
        raise BadFilenameException()
    buf = f.split('.')
    if len(buf)>1:
        return buf[1]
    else:
        return ''

def true_ext(file):
    mime = fm.detect_from_filename(file).mime_type
    if mime in extsDict:
        return extsDict[mime]
    elif mime in extsBlacklist:
        # по-хорошему лучше здесь бросать исключение,
        # и обрабатывать его в check_ext
        # raise FileInBlacklist()
        return "blacklisted"
    else:
        raise NotInDictionaryException()

def check_ext(file):
    extr = true_ext(file)
    if extr == "blacklisted":
        return True
    ext = get_ext(file)
    return extr == ext

def change_ext(file):
    extr = true_ext(file)
    ext = get_ext(file)
    # if not ext:
    if ext != '':
        newpath = Path(str(file)[:-len(ext)]+extr)
    else:
        newpath = Path(str(file)+'.'+extr)
    # у Path есть свой метод rename(), так проще
    # file.rename(newpath)
    os.rename(file, newpath)
    return newpath.parts[-1]

def mime_parser(arr):
    files_to_parse = []
    for x in arr:
        for child in x.iterdir():
            # подсказка от pylint:
            # Comparison to False should be 'not expr'
            if check_ext(child) == False:
                files_to_parse.append(child)
    for file in files_to_parse:
        change_ext(file)
    return 0 # ??? чеэта

def recursive_dirlist_builder(path, arr, count):
    # вообще, мне не нравятся эти приколы с arr и ps.
    # TODO как-нибудь причесать это к одному массиву
    ps = []
    for child in path.iterdir():
        # проверить файл на папку можно и без обращения к magic:
        # if child.is_dir(): ...
        if fm.detect_from_filename(str(child)).mime_type == 'inode/directory':
            ps.append(child)
    arr.extend(ps)
    # можно упростить до невозможного,
    # т.к. bool(0) == False, а bool([]) тоже автоматически ложен
    # if not count or not ps: ...
    if count == 0 or ps == []:
        return arr
    else:
        for x in ps:
            return recursive_dirlist_builder(x, arr, count-1)

# 1. код /исполнения/ скрипта лучше ставить в таком блоке,
# чтобы при `import extfix` они не вызывались
if __name__ == "__main__":
    # 2. метавар необязателен, хотя это и вкусовщина
    parser = argparse.ArgumentParser(description="Utility to fix your files' extensions.")
    parser.add_argument('paths', type=Path, nargs='+', help='Path argument(s)')
    # 3. при вызове метода пробелы между параметром и его значением
    # (help = ...) плохой тон
    parser.add_argument('-d', '--depth', type=int, default=1, help='depth of recursion for directories (default is 1)')
    parser.add_argument('-v', '--verbose', action="store_true", help="shows changes in your files")
    args = parser.parse_args()

    # 4. чтобы не рисковать вляпаться, лучше arr создать как копию от
    # оригинального paths, после чего проходиться по оригиналу.
    # так мы будем уверены, что он не будет меняться во время итерации по нему
    arr = args.paths.copy()
    for x in args.paths:
        arr.extend(recursive_dirlist_builder(x, [], args.depth))
    print(mime_parser(arr))
