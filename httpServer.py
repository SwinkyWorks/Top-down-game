from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import socket
import pygame as pg
import threading
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999
print(socket.gethostname(), HOST)
save = Path("save1.txt")


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text.html")
        self.end_headers()

        self.wfile.write(bytes(Path("save1.txt").read_text(), "utf-8"))

    def do_POST(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        content_length = int(self.headers['Content-Length'])
        result = self.rfile.read(content_length).decode()

        resultSplit = result.split(" ")
        if resultSplit[0] == "attr":
            if len(save.read_text().split("\n")[0].split(", ")) > int(resultSplit[1]):
                if int(resultSplit[2]) > 5 or int(resultSplit[2]) < 0:
                    self.send_response(400)
                    self.wfile.write(
                        bytes('{"response":"Unavailable attribute index"}', "utf-8"))
                lines = save.read_text().split("\n")
                prefix = lines[int(resultSplit[2])].split(": ")[0]
                allAttributeValues = lines[int(resultSplit[2])].split(": ")[
                    1].split(", ")
                allAttributeValues[int(resultSplit[1])] = " ".join(
                    resultSplit[3:])
                lines[int(resultSplit[2])] = prefix + \
                    ": " + ", ".join(allAttributeValues)
                save.write_text("\n".join(lines))
            else:
                self.send_response(400)
                self.wfile.write(
                    bytes('{"response":"Unavailable player index"}', "utf-8"))
        elif resultSplit[0] == "grid":
            try:
                lines = save.read_text().split("\n")
                cells = lines[int(resultSplit[2])+7].split(",")
                cells[int(resultSplit[1])] = " ".join(resultSplit[3:])
                lines[int(resultSplit[2])+7] = ",".join(cells)
                save.write_text("\n".join(lines))
                self.send_response(200)
                self.wfile.write(
                    bytes('{"response":"Request completed"}', "utf-8"))
            except IndexError:
                self.send_response(400)
                self.wfile.write(
                    bytes('{"response":"Out-of-bounds"}', "utf-8"))


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), HTTPRequestHandler)
    print("Server now running...")
    running = True
    pg.init()
    pg.display.set_mode([500, 400])
    threading.Thread(target=server.serve_forever).start()
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
    server.shutdown()
