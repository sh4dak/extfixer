import logging
import sys
from pathlib import Path
import pytest

sys.path.append(str(Path(__file__).parent.parent))
import extfix


JPEG_BIN = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00x"


def pytest_configure():
    # enable debug logging in all tests
    extfix.log.setLevel(logging.DEBUG)


def test_dirbuilder(tmp_path):
    dir1 = tmp_path / "dir1"
    dir2 = dir1 / "dir2"
    dir4 = dir1 / "dir3" / "dir4"
    # create all dirs
    all([x.mkdir(parents=True) for x in (dir1, dir2, dir4)])
    arr = [tmp_path]
    arr.extend(extfix.recursive_dirlist_builder(tmp_path, [], 3))
    assert len(arr) == 5  # five folders in total


@pytest.mark.parametrize("name", ["test.jpeg", "test.tiff", "test.jpg"])
def test_guesser(tmp_path, name):
    jpg = tmp_path / name
    with jpg.open("wb") as fd:
        fd.write(JPEG_BIN)
    assert extfix.true_ext(jpg) == "jpg"
