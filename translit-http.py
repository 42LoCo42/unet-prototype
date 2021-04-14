import sys
import unet_request
import fileserver
import subprocess

def bstrip(line):
    # empty line
    if len(line) == 0:
        return line
    # mac
    if line[-1] == "\r":
        return line[0 : -1]
    # windows
    if line[-2 : len(line)] == "\r\n":
        return line[0 : -2]
    # unix
    if line[-1] == "\n":
        return line[0 : -1]
    # no line ending
    return line

if __name__ == "__main__":
    in_request     = False
    content_length = 0
    headers        = []
    path           = ""
    content        = ""
    while True:
        line = sys.stdin.readline()
        if line == None or len(line) == 0:
            break
        real_len = len(bstrip(line))

        # get section of request
        # at the begining there are headers
        if not in_request:
            in_request = True
            path       = line.split(" ")[1][1:]
            index      = path.find("?")
            if index > -1:
                path, get_params = path[0 : index], path[index + 1 :]
            else:
                get_params = ""
        # save Content-Length
        elif line[0:16] == "Content-Length: ":
            content_length = int(line[16:])
        # after headers comes an empty line...
        elif real_len == 0:
            # and then possibly content...
            if content_length > 0:
                content = sys.stdin.read(content_length)
            in_request = False

        headers += [line]

        # if this request has finished, transliterate and send it
        if not in_request:
            response = fileserver.handle_request(
                unet_request.Request(path, content, get_params, *headers)
            )
            content = response.fields[0]

            NUM = 400
            if not response.is_error:
                NUM = 200
            elif content == "Forbidden":
                NUM = 403
            elif content == "Not Found":
                NUM = 404

            if NUM >= 400:
                content = f"{NUM} - {response.fields[0]}: {response.fields[1]}\n"

            print(content, file = sys.stderr)
            length = len(content)
            p = subprocess.run(
                ["file", "-b", "--mime-type", "-"],
                input = content.encode("utf-8"),
                capture_output = True
            )
            print(f"""\
HTTP/2 {NUM}\r\n\
Content-Length: {length}\r\n\
Content-Type: {p.stdout[0:-1].decode('utf-8')}; charset=utf-8\r\n\
\r\n\
{content}""", end = "")
            break
