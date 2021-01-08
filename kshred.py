#!/usr/bin/env python3

#Written by kelseykm

import os, sys

class Shredder(object):
    """Class for shredding files"""

    def __init__(self, file_object):
        self.file_object = file_object
        self.file_name = file_object.name
        self.file_size = os.stat(file_object.name).st_size
        self.chunk_size = 51200

    def generate_zeros(self, number_to_generate):
        return b'\x00' * number_to_generate

    def generate_ones(self, number_to_generate):
        return b'\x01' * number_to_generate

    def generate_randoms(self, number_to_generate):
        return os.urandom(number_to_generate)

    def number_chunks(self):
        self.number_of_chunks = 0
        def counter():
            while True:
                chunk = self.file_object.read(self.chunk_size)
                if not chunk:
                    return
                yield "chunk"

        for _ in counter():
            self.number_of_chunks += 1

    @property
    def length_of_last_chunk(self):
        self.file_object.seek(0)
        chunks_left = self.number_of_chunks

        while True:
            chunk = self.file_object.read(self.chunk_size)
            if chunks_left == 1:
                return len(chunk)
            chunks_left -= 1

    def shred_file(self):
        self.number_chunks()
        passes = self.number_of_chunks - 1
        last = self.length_of_last_chunk

        #First pass with zeros
        self.file_object.seek(0)
        for _ in range(passes):
            zeros = self.generate_zeros(self.chunk_size)
            self.file_object.write(zeros)
        zeros = self.generate_zeros(last)
        self.file_object.write(zeros)

        #Second pass with ones
        self.file_object.seek(0)
        for _ in range(passes):
            ones = self.generate_ones(self.chunk_size)
            self.file_object.write(ones)
        ones = self.generate_ones(last)
        self.file_object.write(ones)

        #Third pass with randoms
        self.file_object.seek(0)
        for _ in range(passes):
            rands = self.generate_randoms(self.chunk_size)
            self.file_object.write(rands)
        rands = self.generate_randoms(last)
        self.file_object.write(rands)

        #Fourth and last pass with zeros
        self.file_object.seek(0)
        for _ in range(passes):
            zeros = self.generate_zeros(self.chunk_size)
            self.file_object.write(zeros)
        zeros = self.generate_zeros(last)
        self.file_object.write(zeros)

    def delete_file(self):
        os.remove(self.file_name)

def usage():
    instructions = """
Usage: kshred.py <FILE> <FILE> ...

Add the file(s) you want shredded as arguments.

Options:
    -h  Show usage
    """
    print(instructions)
    sys.exit()

def main():
    if not sys.argv[1:] or sys.argv[1] == "-h":
        usage()
    
    for infile in sys.argv[1:]:
        if not os.path.exists(infile):
            print(f"[KSHRED] {infile} DOES NOT EXIST")
            continue
        
        with open(infile, "r+b") as f:
            shredder_obj = Shredder(f)
            shredder_obj.shred_file()
            shredder_obj.delete_file()

if __name__ == "__main__":
    main()
