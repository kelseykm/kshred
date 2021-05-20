#!/usr/bin/env python3

#Written by kelseykm

import os
import sys
import threading
from time import sleep

version = "0.2.1"
normal = '\033[0;39m'
green = '\033[1;32m'
red = '\033[1;31m'
orange = '\033[1;33m'
cycle = "|/-\\"
cycle_stop = False

class Shredder:
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

    @property
    def number_of_chunks(self):            
        if self.file_size == 0:
            return self.file_size
        elif self.file_size != 0 and self.file_size % self.chunk_size != 0:
            return self.file_size // self.chunk_size + 1
        else:
            return self.file_size / self.chunk_size

    @property
    def length_of_last_chunk(self):
        if self.file_size == 0:
            return self.file_size
        elif self.file_size != 0 and self.file_size % self.chunk_size == 0:
            return self.chunk_size
        else:
            return self.file_size % self.chunk_size

    def shred_file(self):
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

def cycler():
    while not cycle_stop:
        for c in cycle:
            sys.stdout.write(f"{green}[INFO]{normal} ")
            sys.stdout.write(f"{orange}[ {normal}{c}{orange} ]")
            sys.stdout.write(f" SHREDDING...{normal}")
            sys.stdout.write("\r")
            sys.stdout.flush()
            sleep(0.5)

def usage():
    instructions = """
Usage: kshred.py <FILE> <FILE> ...

Add the file(s) you want shredded as arguments.
    NB: The files must be regular files.

Options:
    -h  Show usage
    -v  Show version number
    """
    print(instructions)
    sys.exit()

def main():
    if not sys.argv[1:] or sys.argv[1] == "-h":
        usage()
    elif sys.argv[1] == "-v":
        print(f"{green}[INFO]{normal} VERSION {orange}{version}{normal}")
        sys.exit()

    for infile in sys.argv[1:]:
        if not os.path.exists(infile):
            print(f"{red}[ERROR]{normal} {orange}{infile}{normal} DOES NOT EXIST")
            continue
        elif not os.path.isfile(infile):
            print(f"{red}[ERROR]{normal} {orange}{infile}{normal} IS NOT A REGULAR FILE")
            continue

        global cycle_stop
        cycle_stop = False

        thread = threading.Thread(target=cycler)
        thread.start()

        try:
            with open(infile, "r+b") as f:
                shredder_obj = Shredder(f)
                shredder_obj.shred_file()
                shredder_obj.delete_file()
        except:
            cycle_stop = True
            thread.join()
            print(f"{red}[ERROR]{normal} {orange}{infile}{normal} SHREDDING FAILED")
        else:
            cycle_stop = True
            thread.join()
            print(f"{green}[INFO]{normal} {orange}{infile}{normal} SHREDDED SUCCESSFULLY")

if __name__ == "__main__":
    main()
