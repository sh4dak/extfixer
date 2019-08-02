#!/usr/bin/env python3

# System libraries
import argparse
import csv
import logging
from pathlib import Path

# External libraries
import magic as fm


log = logging.getLogger(__name__)

#exts_dict = {
#    "image/png": "png",
#    "image/gif": "gif",
#    "image/jpeg": "jpg",
#    "text/html": "html",
#    "application/zip": "zip",
#    "application/vnd.rar": "rar",
#    "application/x-7z-compressed": "7z",
#}

with open('extensions.csv', mode='r') as file:
    reader = csv.reader(file)
    exts_dict = {rows[0]:rows[1] for rows in reader}
print(exts_dict)


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


class FileFixer:
    def __init__(self, file: Path):
        self.file = file
        if any(i in file.name for i in FILENAME_PROHIBITED):
            raise BadFilenameException(file)

    def current_extension(self) -> str:
        return self.file.suffix[1:]

    def real_extension(self) -> str:
        if self.file.is_dir():
            raise IsADirectoryError(self.file)
        mime = fm.detect_from_filename(self.file).mime_type
        true_ext = exts_dict.get(mime)
        if true_ext:
            log.info("Real extension: %s", exts_dict[mime])
            return true_ext
        raise NotInDictionaryException(self.file)

    def extension_correct(self):
        """
        Returns True if extension is correct,
        otherwise returns real extension.
        """
        real_ext = self.real_extension()
        if real_ext == "blacklisted" or real_ext == self.current_extension():
            return True
        return real_ext

    def change_ext(self, ext: str):
        log.info("Processing file %s", self.file)
        ext = self.real_extension()
        file_noext = self.file.stem  # имя файла, без последнего расширения
        newpath = self.file.parent / f"{file_noext}.{ext}"
        log.info("Renaming to %s", newpath.name)
        self.file.rename(newpath)

    def fix(self):
        real = self.extension_correct()
        if real is not True:
            self.change_ext(real)

    # для корректного отображения объекта при дебаге
    def __repr__(self):
        return f"FileFixer({self.file!r})"

def recursive_dirlist_builder(path, arr, count):
    # вообще, мне не нравятся эти приколы с arr и ps.
    # TODO как-нибудь причесать это к одному массиву
    ps = []
    for child in path.iterdir():
        if child.is_dir():
            log.info("Appending %s directory to the search list", child)
            ps.append(child)
    arr.extend(ps)
    if not count or not ps:
        return arr
    else:
        for x in ps:
            log.info("Going into folder %s", x)
            return recursive_dirlist_builder(x, arr, count - 1)

def fix_all(directories):
    files = []
    for dir in directories:
        for child in dir.iterdir():
            if child.is_dir():
                continue
            log.info("Appending %s file to the search list", child)
            files.append(child)
    for file in files:
        FileFixer(file).fix()


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
    fix_all(arr)
    log.info("Done.")
