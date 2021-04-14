import atexit
import queue
import socket
import sys
from enum import Enum
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

TCP_IP = sys.argv[1]
TCP_PORT = int(sys.argv[2])

BUFSIZE = 4096

def exit_handler():
    print("Closing server")
    tcp_server.close()
    print("Waiting for handlers to close")
    for t in threads:
        t.join()
    atexit.unregister(exit_handler)

atexit.register(exit_handler)

tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcp_server.bind((TCP_IP, TCP_PORT))
print("Server started")

class MsgType(Enum):
    CLIENT = 1
    SERVER = 2

def threaded_read(queue, ident, source, *args):
    while True:
        try:
            data = source(*args)
            if len(data) < 1:
                queue.put((ident, None))
                break
            queue.put((ident, data))
        except Exception as e:
            print(e)
            break

class Handler(Thread):
    def __init__(self, conn_obj):
        Thread.__init__(self)
        (self.conn, (self.ip, self.port)) = conn_obj

    def run(self):
        try:
            p = Popen(sys.argv[3:],
                stdin = PIPE, stdout = PIPE, stderr = sys.stderr,
                bufsize = 0
            )
            q = queue.Queue()
            client_reader = Thread(target = threaded_read, args = (
                q, MsgType.CLIENT, self.conn.recv, BUFSIZE
            ))
            server_reader = Thread(target = threaded_read, args = (
                q, MsgType.SERVER, p.stdout.read, BUFSIZE
            ))
            # the readers should exit with us
            client_reader.daemon = True
            server_reader.daemon = True
            client_reader.start()
            server_reader.start()
            running = 2

            print(f"\nNew handler started for {self.ip}:{self.port}")
            while running > 0:
                (ident, data) = q.get()
                if ident == MsgType.CLIENT:
                    if data == None:
                        p.stdin.close()
                        running -= 1
                        print("Client exited")
                    else:
                        # print(f"{data} → server")
                        p.stdin.write(data)
                        p.stdin.flush()
                elif ident == MsgType.SERVER:
                    if data == None:
                        p.stdin.close()
                        p.stdout.close()
                        running -= 2
                        print("Server exited")
                    else:
                        # print(f"{data} → client")
                        self.conn.send(data)

            p.wait()
        except FileNotFoundError as e:
            print(f"Handler could not be started: Subprocess command not found\n{e}")
        finally:
            self.conn.close()
            print(f"Handler closed for {self.ip}:{self.port}")


threads = []
while True:
    try:
        tcp_server.listen(5)
        conn_obj = tcp_server.accept()
        newthread = Handler(conn_obj)
        newthread.start()
        threads.append(newthread)
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("Exiting")
        break

exit_handler()
