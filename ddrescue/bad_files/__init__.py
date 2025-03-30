import sys

from ddrescue.bad_files.file import File
from ddrescue.bad_files.backends.pycdlib import PyCdlib
from ddrescue import Map

def run():
    with open(sys.argv[2], mode='r') as file:
        rescue = Map.parse(file)

    if rescue.is_finished():
        return 0

    bad_files = {}
    backend = PyCdlib

    with open(sys.argv[1], mode='rb') as image:
        with backend(image) as file_system:
            for path, start, end in file_system.walk():

                match = rescue.bad_blocks[start:end]
                if match:
                    if path not in bad_files:
                        bad_files[path] = File(path, start, end)

                    bad_file = bad_files[path]
                    corrupt_blocks = [block.data for block in list(match)]
                    bad_file.corrupt_blocks.extend(corrupt_blocks)

    for file in bad_files.values():
        print('{:6.2f}% {}'.format(file.corruption_percentage(), file.path))
