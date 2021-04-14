import sys
import os

def byte(value):
    return value.to_bytes(1, byteorder = "big")

def has_method(obj, name):
    return hasattr(obj, name) and callable(getattr(obj, name))

# common print modifications

def print_raw(text):
    sys.stdout.buffer.write(text)

def print_err(*args, **kwargs):
    print(file = sys.stderr, *args, **kwargs)

# checks on files

def in_directory(file, directory):
    directory = os.path.realpath(directory)
    file      = os.path.realpath(file)
    return os.path.commonprefix((directory, file)) == directory

def is_executable(file):
    return os.path.isfile(file) and os.access(file, os.X_OK)

def is_readable(file):
    return os.path.isfile(file) and os.access(file, os.R_OK)

# typical exceptions

class SecurityViolation(Exception):
    pass

class InvalidRequest(Exception):
    pass

