#!/usr/bin/env python3

# System libraries
import argparse
from pathlib import Path
import logging

# External libraries
import magic as fm


log = logging.getLogger(__name__)

exts_dict = {
    "image/png": "png",
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "text/html": "html",
    "application/zip": "zip",
    "application/vnd.rar": "rar",
    "application/x-7z-compressed": "7z",
}


class BadFilenameException(Exception):
    pass


class NotInDictionaryException(Exception):
    pass


class ArgumentException(Exception):
    pass


# если создать массив через фигурные скобки,
# типа как словарь без значений, то получится множество (set),
# к которому операция `x in set(...)` проходит гораздо быстрее
FILENAME_PROHIBITED = {"<", ">", ":", '"', "\\", "|", "?", "*"}


def get_ext(file):
    # если нужно получить из пути имя файла:
    # print(file.name)
    name = file.parts[-1]
    if any(i in name for i in FILENAME_PROHIBITED):
        raise BadFilenameException()
    buf = name.split(".")
    if len(buf) > 1:
        # что, если у файла два расширения (.tar.gz)?
        return buf[1]
    else:
        return ""


def true_ext(file):
    mime = fm.detect_from_filename(file).mime_type
    # у dict есть метод .get(), который возвращает значение,
    # или None, если такого ключа не нашлось
    # фишка в том, что он не бросает исключение при неудаче,
    # и None можно с лёгкостью проверить в if
    # здесь это не критично, но на будущее вот
    # true_ext = exts_dict.get(mime)
    # if true_ext:
    #     return true_ext
    if mime in exts_dict:
        log.info("Real extension: %s", exts_dict[mime])
        return exts_dict[mime]
    else:
        raise NotInDictionaryException()


def check_ext(file):
    extr = true_ext(file)
    if extr == "blacklisted":
        return True
    ext = get_ext(file)
    return extr == ext


def change_ext(file: Path):
    log.info("Processing file %s", file)
    extr = true_ext(file)
    ext = get_ext(file)
    breakpoint()
    file_noext = file.stem # имя файла, без последнего расширения
    newpath = file.parent /  f"{file_noext}.{extr or ext}"
    log.info("Renaming to %s", newpath.name)
    file.rename(newpath)


def mime_parser(arr):
    files_to_parse = []
    for x in arr:
        for child in x.iterdir():
            if not check_ext(child):
                files_to_parse.append(child)
    for file in files_to_parse:
        change_ext(file)
    return "Finished."


def recursive_dirlist_builder(path, arr, count):
    # вообще, мне не нравятся эти приколы с arr и ps.
    # TODO как-нибудь причесать это к одному массиву
    ps = []
    for child in path.iterdir():
        if child.is_dir():
            log.info("Appending %s to the search list", child)
            ps.append(child)
    arr.extend(ps)
    if not count or not ps:
        return arr
    else:
        for x in ps:
            log.info("Going into folder %s", x)
            return recursive_dirlist_builder(x, arr, count - 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Utility to fix your files' extensions."
    )
    parser.add_argument("paths", type=Path, nargs="+", help="Path argument(s)")
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1,
        help="depth of recursion for directories (default is 1)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="shows changes in your files"
    )
    args = parser.parse_args()

    # формат сообщений в логе. полный перечень переменных здесь:
    # https://docs.python.org/3/library/logging.html#logrecord-attributes
    log_format = "%(levelname)s %(message)s"
    logging.basicConfig(format=log_format)
    # если передали --verbose, то логгер выводит
    # все сообщения уровнем INFO и выше,
    # в остальных случаях сообщаем только о WARN и ERROR
    log.setLevel(logging.INFO if args.verbose else logging.WARN)

    arr = args.paths.copy()
    for x in args.paths:
        arr.extend(recursive_dirlist_builder(x, [], args.depth))
    log.info("Done.")
    mime_parser(arr)
