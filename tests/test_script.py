import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import extfix


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
    assert len(arr) == 5 # five folders in total
