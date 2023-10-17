from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import socket
import pygame as pg
import threading
import time

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9999
print(socket.gethostname(), HOST)
save = Path("saves/save1.txt")


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text.html")
        self.end_headers()
        content_length = 0
        try:
            content_length = self.headers['Content-Length']
        except TypeError:
            content_length = 0
        if content_length == None:
            content_length = 0
        result = self.rfile.read(content_length).decode()
        resultSplit = result.split(" ")

        if resultSplit[0] != "joinPlayerTest":  # joinPlayerTest [username]
            self.send_response(200)
            self.wfile.write(bytes(save.read_text(), "utf-8"))
        else:
            print("Join player test: " + resultSplit[1])
            if resultSplit[1] in save.read_text().split("\n")[0][9:].split(", "):
                self.send_response(200)
                self.wfile.write(
                    bytes("1", "utf-8"))
            else:
                self.send_response(200)
                self.wfile.write(
                    bytes("0", "utf-8"))

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
                self.wfile.write(
                    bytes('{"response":"Request completed"}', "utf-8"))
            else:
                self.send_response(400)
                self.wfile.write(
                    bytes('{"response":"Unavailable player index"}', "utf-8"))
        elif resultSplit[0] == "grid":  # grid [username] [color]
            try:
                lines = save.read_text().split("\n")
                cells = lines[int(resultSplit[2])+8].split(",")
                cells[int(resultSplit[1])] = " ".join(resultSplit[3:])
                lines[int(resultSplit[2])+7] = ",".join(cells)
                save.write_text("\n".join(lines))
                self.wfile.write(
                    bytes('{"response":"Request completed"}', "utf-8"))
            except IndexError:
                self.send_response(400)
                self.wfile.write(
                    bytes('{"response":"Out-of-bounds"}', "utf-8"))
        elif resultSplit[0] == "joinPlayer":  # joinPlayer [username] [color]
            lines = save.read_text().split("\n")
            defaultAtributes = lines[6][20:].split(", ")
            if len(lines[0].split(": ")[1]) == 1:
                lines[0] += resultSplit[1]  # Username
                lines[1] += defaultAtributes[0]  # Location
                lines[2] += defaultAtributes[1]  # Inventory
                lines[3] += defaultAtributes[2]  # Last signal
                lines[4] += resultSplit[2]  # Color
                lines[3] += defaultAtributes[3]  # Direction
            else:
                lines[0] += ", " + resultSplit[1]  # Username
                lines[1] += ", " + defaultAtributes[0]  # Location
                lines[2] += ", " + defaultAtributes[1]  # Inventory
                lines[3] += ", " + defaultAtributes[2]  # Last signal
                lines[4] += ", " + resultSplit[2]  # Color
                lines[3] += ", " + defaultAtributes[3]  # Direction
            save.write_text("\n".join(lines))
            self.wfile.write(
                bytes('{"response":"Request completed"}', "utf-8"))


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
