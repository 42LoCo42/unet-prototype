from   functools import reduce
from   math      import floor, log
from   common    import byte, has_method, print_raw

class Request():
    def __init__(self, *fields, is_error = False):
        # save data for easy access
        self.is_error = is_error
        self.fields = list(fields)
        # build initial value
        self.build()

    def build(self):
        needs_encode = has_method(self.fields[0], "encode")
        nullbyte     = '\0' if needs_encode else b'\0'
        self.data    = reduce(
            lambda x, y: x + nullbyte + y,
            self.fields[1:], self.fields[0]
        )
        if not needs_encode:
            self.fields = list(map(lambda x: x.decode("utf-8"), self.fields))
        data_length = len(self.data)
        head_length = floor(log(data_length, 256)) + 1
        self.data \
            = (b'\0' if self.is_error else b'') \
            + byte(head_length) \
            + data_length.to_bytes(head_length, byteorder = "big") \
            + self.data.encode("utf-8") if needs_encode else self.data

    def print(self, *args, **kwargs):
        pretty_type = "Err: " if self.is_error else "Data:"
        print(f"{pretty_type} {self.fields}", *args, **kwargs)

    def print_raw(self):
        print_raw(self.data)

    @staticmethod
    def from_raw(raw):
        needs_encode = has_method(raw, "encode")
        raw = raw.encode("utf-8") if needs_encode else raw
        if len(raw) < 1:
            raise ValueError("Needs header length byte!")
        head_length, raw = raw[0], raw[1:]
        is_error = False
        if head_length == 0:
            is_error = True
            head_length, raw = raw[0], raw[1:]
        if len(raw) < head_length:
            raise ValueError(f"Needs {head_length} bytes of header!")
        data_length, raw = int.from_bytes(raw[0: head_length], "big"), raw[head_length:]
        if len(raw) < data_length:
            raise ValueError(f"Needs {data_length} bytes of data!")
        data, raw = raw[0: data_length], raw[data_length:]
        return Request(*data.split(b'\0'), is_error = is_error), raw
