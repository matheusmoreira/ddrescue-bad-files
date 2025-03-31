from ddrescue.bad_files.backend import Backend

import pycdlib

class PyCdlib(Backend):
    def __init__(self, image):
        self.pycdlib = pycdlib.PyCdlib()
        self.pycdlib.open_fp(image)

    def close(self):
        self.pycdlib.close()

    def get_inode_from(file):
        return file._ctxt.ino

    def walk(self):
        for path, directories, files in self.pycdlib.walk(iso_path='/'):
            for filename in files:

                full_path = path + '/' + filename

                with self.pycdlib.open_file_from_iso(iso_path=full_path) as file:

                    inode = PyCdlib.get_inode_from(file)
                    start = inode.extent_location() * self.pycdlib.logical_block_size
                    size = inode.get_data_length()
                    end = start + size

                    yield full_path, start, end
