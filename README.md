# unet-prototype
µnet, a network protocol and architecture following the UNIX philosophy.
## What and why?
Many protocols are just different ways of accessing files on a server.
I want to unify them under a common and extremely simple protocol while also regaining the benefits of the UNIX philosophy,
primarily the common text stream interface.

µnet is separated into some core and arbitrarily many transliteration units.
It reads or executes files, making integration of other programs trivial (no new code must be written to support a specific file type).

A µnet packet has the following structure:
- 1 byte: Header length `h`: How many bytes of header will follow
- `h` bytes: Content length `c`: How many bytes of content will follow
- `c` bytes: Content: Separated by nullbytes into fields

Most transliteration units will arrange the original request's data as fields of this order:
- Path of the accessed resource
- Content (e.g. body of POST), will be passed as stdin to executable resources
- Path parameters: e.g. the `id=42&gizmo=active` text after `GET /foo`,
will be the first argument of executable resources
- All headers of the request as the following arguments
## Test
The HTTP server can be run like this:
```bash
python main.py localhost 37812 python translit-http.py
```
In another terminal, run the following command to be greeted:
```
curl "localhost:37812/greet?name=J.%20Random%20Hacker"
```
## TODO
- Allow executable resources to specify their own headers, possibly dependant on the transliteration unit protocol.
