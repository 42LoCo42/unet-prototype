import sys
import traceback
import subprocess
import unet_request
from common import (
    print_err,
    in_directory,
    is_readable,
    is_executable,
    InvalidRequest,
    SecurityViolation
)

def handle_err(request):
    raise InvalidRequest("A client may not send error requests!")

def handle_dat(request):
    allowed_directory = "global/"
    file = allowed_directory + request.fields[0]
    args = request.fields[2:]
    if not in_directory(file, allowed_directory):
        raise SecurityViolation("Forbidden", request.fields[0])
    if is_executable(file):
        p = subprocess.run(
            [file] + args,
            input =
                request.fields[1].encode("utf-8")
                if len(request.fields) >= 1
                else b'',
            capture_output = True
        )
        if len(p.stderr) > 0:
            print_err("stderr: " + p.stderr.decode("utf-8"))
        return unet_request.Request(p.stdout)
    elif is_readable(file):
        with open(file, "rb") as f:
            return unet_request.Request(f.read())
    else:
        raise InvalidRequest("Not Found", file[len(allowed_directory) - 1:])

def handle_request(request):
    print_err("access: " + request.fields[0])
    print_err("params: " + request.fields[2])
    try:
        if request.is_error:
            return handle_err(request)
        else:
            return handle_dat(request)
    except (SecurityViolation, InvalidRequest) as e:
        fields = map(str, e.args)
        return unet_request.Request(*fields, is_error = True)
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    raw = sys.stdin.buffer.raw.read(8192)
    while len(raw) > 0:
        try:
            req, raw = unet_request.Request.from_raw(raw)
            handle_request(req).print_raw()
        except ValueError as e:
            raw = ""
            fields = map(str, e.args)
            unet_request.Request(*fields, is_error = True).print_raw()
