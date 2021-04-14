import socket

with socket.socket() as s:
    s.connect(("localhost", 37812))
    s.send(b"foo")
    print(s.recv(4096))
