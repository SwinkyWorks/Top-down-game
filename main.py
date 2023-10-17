import pygame as pg
from pathlib import Path
from datetime import datetime
from random import random
from cProfile import Profile
from httpServer import HTTPServer, HTTPRequestHandler
import socket
import requests
import threading
from time import time_ns

pg.init()
screen = pg.display.set_mode((1366, 768), pg.RESIZABLE)


def drawText(text, font, size, pos, color, lineSeperation=0, saveArray: list = None):
    text = str(text).split("\n")
    size = round(size)
    font = pg.font.Font(font, size)
    lineNum = 0
    for line in text:
        txt_surface = font.render(line, True, color)
        screen.blit(txt_surface, (pos[0], pos[1] +
                    (lineNum*(size+lineSeperation))))
        lineNum += 1


def drawImage(src, pos, size=None, smoothScale=False):
    image = None
    # print(type(src))
    colorkey = None
    if not isinstance(src, pg.Surface):
        image = pg.image.load(src).convert_alpha()
    else:
        image = src

    colorkey = image.get_colorkey()
    image.set_colorkey(None)
    scaled_image = None
    if size and size[0] != image.get_width() and size[1] != image.get_height():
        if smoothScale:
            scaled_image = pg.transform.smoothscale(image, size)
        else:
            scaled_image = pg.transform.scale(image, size)
    else:
        scaled_image = image
    image.set_colorkey(colorkey)

    screen.blit(scaled_image, pos)


def indexInArray(array: list, val):
    """Gets the index of a value in an array."""
    try:
        return array.index(val)
    except ValueError:
        return int(-1)


def indexOfPlayerImage(color, direction):
    return indexInArray(["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "White"], color) * 4 + indexInArray(["Up", "Left", "Down", "Right"], direction)


if False:
    """
        1111111111

        11111
        11111

        11
        11
        11
        11
        11

        1
        1
        1
        1
        1
        1
        1
        1
        1
        1

    """
    print("00:00;"*10)


save = Path("saves/save1.txt")


def setAttribute(playerIndex: int, attr: int, value: str):
    if len(save.read_text().split("\n")[0].split(", ")) > playerIndex:
        if attr > 5 or attr < 0:
            raise IndexError("There is no attribute of that index!")
        lines = save.read_text().split("\n")
        prefix = lines[attr].split(": ")[0]
        allAttributeValues = lines[attr].split(": ")[1].split(", ")
        allAttributeValues[playerIndex] = value
        lines[attr] = prefix + ": " + ", ".join(allAttributeValues)
        save.write_text("\n".join(lines))
    else:
        raise IndexError("There is no player of that index!")


def setBlock(x: int, y: int, value: str):
    lines = save.read_text().split("\n")
    cells = lines[y+8].split(",")
    cells[x] = value
    lines[y+8] = ",".join(cells)
    save.write_text("\n".join(lines))


runningInEditor = True
server_running = False
server = HTTPServer((socket.gethostbyname(
    socket.gethostname()), 0), HTTPRequestHandler)
try:
    def run():
        global server_running, server
        acceptedUsernameText = "abcdefghijklmnopqrstuvwxyz1234567890-_"
        cellSize = 200
        screenPos = [0, 0]
        currentPos = [20, 20]
        textToLog = ""
        pg.FULLSCREEN = False

        running = True

        mainMenu = True
        paused = False
        invOpen = False

        clock = pg.time.Clock()
        size = screen.get_size()
        dt = 0
        pos = None
        inv = None
        playerDir = None
        grid = None
        name = Path("savedData.txt").read_text().split("\n")[0][10:]
        preferredColor = Path("savedData.txt").read_text().split("\n")[1][7:]
        maxMovementDelay = 0.333
        movementDelay = 0
        maxClickDelay = 0.033
        clickDelay = 0
        keys = [False] * 200
        invCellSize = 100
        invBarWidth = invCellSize*(5.3)
        invBarHeight = invCellSize*(1.1)
        invBarBottomOffset = 80
        allPlayerImages = []
        allBlockImages = [
            {"name": "Dirt", "path": "Images/Blocks/dirt.png",
                "data": pg.Surface((80, 80))},
            {"name": "Grass", "path": "Images/Blocks/grass.png",
                "data": pg.Surface((80, 80))},
            {"name": "Sand", "path": "Images/Blocks/sand.png",
                "data": pg.Surface((80, 80))},
            {"name": "Stone", "path": "Images/Blocks/stone.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood door e", "path": "Images/Blocks/wood door e.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood door n", "path": "Images/Blocks/wood door n.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood door s", "path": "Images/Blocks/wood door s.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood door w", "path": "Images/Blocks/wood door w.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood floor", "path": "Images/Blocks/wood floor.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood", "path": "Images/Blocks/wood.png",
                "data": pg.Surface((80, 80))},
        ]
        allInvImages = [
            {"name": "Dirt", "path": "Images/Blocks/dirt.png",
                "data": pg.Surface((80, 80))},
            {"name": "Sand", "path": "Images/Blocks/sand.png",
                "data": pg.Surface((80, 80))},
            {"name": "Stone", "path": "Images/Blocks/stone.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood door", "path": "Images/Blocks/wood door n.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood floor", "path": "Images/Blocks/wood floor.png",
                "data": pg.Surface((80, 80))},
            {"name": "Wood", "path": "Images/Blocks/wood.png",
                "data": pg.Surface((80, 80))}
        ]
        allUiImages = [
            {"name": "Inventory bar", "path": "Images/UI/Invbar.png",
                "data": pg.Surface((106, 22))},
        ]
        allBlocks = [
            "Dirt",
            "Grass",
            "Sand",
            "Stone",
            "Wood door e",
            "Wood door n",
            "Wood door s",
            "Wood door w",
            "Wood floor",
            "Wood"
        ]
        allItems = [
            "Dirt",
            "Sand",
            "Stone",
            "Wood door",
            "Wood floor",
            "Wood"
        ]
        for color in ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet", "White"]:
            for dir in ["Up", "Left", "Down", "Right"]:
                allPlayerImages.append(
                    {"dir": dir, "color": color, "data": pg.Surface((36, 36))})
                allPlayerImages[len(allPlayerImages)-1]["data"].fill(color)
                allPlayerImages[len(allPlayerImages)-1]["data"].blit(
                    pg.image.load("Images/Characters/" + dir + ".png"), (0, 0))
        for i in range(len(allBlockImages)):
            allBlockImages[i]["data"].fill((255, 255, 255))
            allBlockImages[i]["data"].blit(
                pg.image.load(allBlockImages[i]["path"]), (0, 0))
        for i in range(len(allInvImages)):
            allInvImages[i]["data"].fill((255, 255, 255))
            allInvImages[i]["data"].blit(
                pg.image.load(allInvImages[i]["path"]), (0, 0))
        for i in range(len(allUiImages)):
            allUiImages[i]["data"].blit(
                pg.image.load(allUiImages[i]["path"]), (0, 0))

        prevClickData = pg.mouse.get_pressed()
        prevKeyData = pg.key.get_pressed()
        showLog = False
        screenShake = 0
        numberImages = []
        numberFont = None  # "Images/UI/Numbers.ttf"
        currentInvCell = int(0)
        currentInvScreenCell = [0, 0]
        maxInvMoveDelay = 0.2
        invMoveDelay = 0
        maxInvClickDelay = 0.033
        invClickDelay = 0
        invHoldingItemstack = ""
        savedRotation = None
        data = ""
        lines = []
        players = []
        locations = []
        playerPrevPositions = []
        mostRecentPlayerPositions = []
        playerAnims = []
        maxPlayerAnim = 0.333
        SERVERMODE = "none"
        host = ""
        port = ""
        pg.display.flip()

        # try:
        while running:
            if not mainMenu:
                for event in pg.event.get():
                    if event.type == pg.MOUSEWHEEL:
                        currentInvCell = (
                            currentInvCell - event.precise_y) % 5
                    elif event.type == pg.QUIT:
                        running = False
                        if server_running:
                            server.shutdown()
                            server_running = False
                if movementDelay > 0:
                    movementDelay -= dt
                if clickDelay > 0:
                    clickDelay -= dt
                if invMoveDelay > 0:
                    invMoveDelay -= dt
                if invClickDelay > 0:
                    invClickDelay -= dt
                screen.fill(pg.Color(0, 0, 0, 255))
                if SERVERMODE == "join":
                    data = requests.get(
                        "http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/").text
                else:
                    data = save.read_text()
                if not data:
                    continue
                lines = data.split("\n")
                players = lines[0][9:].split(", ")
                locations = lines[1][11:].split(", ")
                inventories = lines[2][13:].split(", ")
                lastActions = lines[3][14:].split(", ")
                colors = lines[4][8:].split(", ")
                directions = lines[5][12:].split(", ")
                grid = lines[8:]
                if len(players) > len(playerPrevPositions):
                    for i in range(len(players) - len(playerPrevPositions)):
                        playerPrevPositions.append(locations[i])
                        mostRecentPlayerPositions.append(locations[i])
                        playerAnims.append(0)
                newGrid = []
                if playerPrevPositions:
                    for i in range(len(players)):
                        playerAnims[i] -= dt if playerAnims[i] > 0 else 0
                        playerAnims[i] = 0 if playerAnims[i] < 0 else playerAnims[i]

                        if str(playerPrevPositions[i]) != str(locations[i]):
                            playerAnims[i] = maxPlayerAnim
                            mostRecentPlayerPositions[i] = playerPrevPositions[i]
                y = 0
                for line in grid:
                    newGrid.append([])
                    x = 0
                    for cell in line.split(","):
                        newGrid[len(newGrid)-1].append(cell)
                        if cellSize*(x+1)+screenPos[0] >= 0 and cellSize*x+screenPos[0] <= pg.display.get_window_size()[0] and cellSize*(y+1)+screenPos[1] >= 0 and cellSize*y+screenPos[1] <= pg.display.get_window_size()[1]:
                            if cell in "Grass//Dirt//Sand//Stone//Wood floor//Wood":
                                drawImage(allBlockImages[allBlocks.index(
                                    cell)]["data"], (cellSize*x+screenPos[0], cellSize*y+screenPos[1]), (cellSize, cellSize))
                            elif cell[:10] == "Wood door:":
                                if cell[11:12] == "c":
                                    drawImage(allBlockImages[allBlocks.index("Wood door " + cell[10:11])]["data"], (
                                        cellSize*x+screenPos[0], cellSize*y+screenPos[1]), (cellSize, cellSize))
                                else:
                                    cellDir = cell[10:11]
                                    if cellDir == "n":
                                        cellDir = "e"
                                    elif cellDir == "e":
                                        cellDir = "s"
                                    elif cellDir == "s":
                                        cellDir = "w"
                                    elif cellDir == "w":
                                        cellDir = "n"
                                    drawImage(allBlockImages[allBlocks.index("Wood door " + cellDir)]["data"], (
                                        cellSize*x+screenPos[0], cellSize*y+screenPos[1]), (cellSize, cellSize))
                        x += 1
                    y += 1
                keys = pg.key.get_pressed()
                if name in players:
                    index = indexInArray(players, name)
                    time = time_ns()
                    if SERVERMODE == "join":
                        requests.post("http://" + host[0] + ".".join(
                            list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 3 {time}")
                    else:
                        setAttribute(index, 3, str(time))
                    pos = locations[index].split(":")
                    pos[0] = int(pos[0])
                    pos[1] = int(pos[1])
                    # if keys[pg.K_u]:
                    #     screenShake += dt*5
                    # if keys[pg.K_j] and screenShake - dt*5 >= 0:
                    #     screenShake -= dt*5
                    topOffset = -1/maxPlayerAnim * playerAnims[index]
                    leftOffset = -1/maxPlayerAnim * playerAnims[index]
                    topOffset *= int(
                        mostRecentPlayerPositions[index].split(":")[1]) - pos[1]
                    leftOffset *= int(
                        mostRecentPlayerPositions[index].split(":")[0]) - pos[0]
                    screenPos[0] = -min(max((pos[0]+0.5-leftOffset)*cellSize - pg.display.get_window_size()[
                        0]/2, 0), cellSize*len(newGrid[0])-pg.display.get_window_size()[0]) + (random() - 0.5) * screenShake
                    screenPos[1] = -min(max((pos[1]+0.5-topOffset)*cellSize - pg.display.get_window_size()[
                        1]/2, 0), cellSize*len(newGrid)-pg.display.get_window_size()[1]) + (random() - 0.5) * screenShake
                    inv = inventories[index].split(";")
                    invHoldingItemstack = inv[10]
                    playerDir = directions[index]
                    if movementDelay <= 0:
                        if not invOpen:
                            if keys[pg.K_w] or keys[pg.K_UP]:
                                movementDelay += maxMovementDelay
                                playerDir = "Up"
                                if SERVERMODE in "singleplayer,host":
                                    setAttribute(index, 5, playerDir)
                                else:
                                    requests.post("http://" + host[0] + ".".join(
                                        list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 5 {playerDir}")

                                canMove = True

                                if (pos[1] <= 0
                                    or newGrid[pos[1]-1][pos[0]] in "Dirt//Sand//Stone//Wood"
                                    or (
                                        newGrid[pos[1]-1][pos[0]
                                                          ][:10] == "Wood door:"
                                        and (newGrid[pos[1]-1][pos[0]][10:] == "sc"
                                             or newGrid[pos[1]-1][pos[0]][10:] == "eo")
                                )
                                    or (
                                        newGrid[pos[1]][pos[0]
                                                        ][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]][10:] == "nc"
                                             or newGrid[pos[1]][pos[0]][10:] == "wo")
                                )):
                                    canMove = False

                                if canMove:
                                    pos[1] -= 1
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(
                                            index, 1, f"{pos[0]}:{pos[1]}")
                                    else:
                                        requests.post("http://" + host[0] + ".".join(list(
                                            host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 1 {pos[0]}:{pos[1]}")
                            if keys[pg.K_a] or keys[pg.K_LEFT]:
                                movementDelay += maxMovementDelay
                                playerDir = "Left"
                                if SERVERMODE in "singleplayer,host":
                                    setAttribute(index, 5, playerDir)
                                else:
                                    requests.post("http://" + host[0] + ".".join(
                                        list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 5 {playerDir}")

                                canMove = True

                                if (pos[0] <= 0
                                    or newGrid[pos[1]][pos[0]-1] in "Dirt//Sand//Stone//Wood"
                                    or (
                                        newGrid[pos[1]][pos[0] -
                                                        1][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]-1][10:] == "ec"
                                             or newGrid[pos[1]][pos[0]-1][10:] == "no")
                                )
                                    or (
                                        newGrid[pos[1]][pos[0]
                                                        ][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]][10:] == "wc"
                                             or newGrid[pos[1]][pos[0]][10:] == "so")
                                )):
                                    canMove = False

                                if canMove:
                                    pos[0] -= 1
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(
                                            index, 1, f"{pos[0]}:{pos[1]}")
                                    else:
                                        requests.post("http://" + host[0] + ".".join(list(
                                            host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 1 {pos[0]}:{pos[1]}")
                            if keys[pg.K_s] or keys[pg.K_DOWN]:
                                movementDelay += maxMovementDelay
                                playerDir = "Down"
                                if SERVERMODE in "singleplayer,host":
                                    setAttribute(index, 5, playerDir)
                                else:
                                    requests.post("http://" + host[0] + ".".join(
                                        list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 5 {playerDir}")

                                canMove = True

                                if (pos[1] >= len(newGrid)-1
                                    or newGrid[pos[1]+1][pos[0]] in "Dirt//Sand//Stone//Wood"
                                    or (
                                        newGrid[pos[1]+1][pos[0]
                                                          ][:10] == "Wood door:"
                                        and (newGrid[pos[1]+1][pos[0]][10:] == "nc"
                                             or newGrid[pos[1]+1][pos[0]][10:] == "wo")
                                )
                                    or (
                                        newGrid[pos[1]][pos[0]
                                                        ][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]][10:] == "sc"
                                             or newGrid[pos[1]][pos[0]][10:] == "eo")
                                )):
                                    canMove = False

                                if canMove:
                                    pos[1] += 1
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(
                                            index, 1, f"{pos[0]}:{pos[1]}")
                                    else:
                                        requests.post("http://" + host[0] + ".".join(list(
                                            host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 1 {pos[0]}:{pos[1]}")
                            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                                movementDelay += maxMovementDelay
                                playerDir = "Right"
                                if SERVERMODE in "singleplayer,host":
                                    setAttribute(index, 5, playerDir)
                                else:
                                    requests.post("http://" + host[0] + ".".join(
                                        list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 5 {playerDir}")

                                canMove = True

                                if (pos[0] >= len(newGrid[0])-1
                                    or newGrid[pos[1]][pos[0]+1] in "Dirt//Sand//Stone//Wood"
                                    or (
                                        newGrid[pos[1]][pos[0] +
                                                        1][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]+1][10:] == "wc"
                                             or newGrid[pos[1]][pos[0]+1][10:] == "so")
                                )
                                    or (
                                        newGrid[pos[1]][pos[0]
                                                        ][:10] == "Wood door:"
                                        and (newGrid[pos[1]][pos[0]][10:] == "ec"
                                             or newGrid[pos[1]][pos[0]][10:] == "no")
                                )):
                                    canMove = False

                                if canMove:
                                    pos[0] += 1
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(
                                            index, 1, f"{pos[0]}:{pos[1]}")
                                    else:
                                        requests.post("http://" + host[0] + ".".join(list(
                                            host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 1 {pos[0]}:{pos[1]}")
                    if invOpen:
                        if invMoveDelay <= 0:
                            if keys[pg.K_w] or keys[pg.K_UP]:
                                invMoveDelay += maxInvMoveDelay
                                currentInvScreenCell[1] += 1
                                if currentInvScreenCell[1] > 1:
                                    currentInvScreenCell[1] = 1
                            if keys[pg.K_a] or keys[pg.K_LEFT]:
                                invMoveDelay += maxInvMoveDelay
                                currentInvScreenCell[0] -= 1
                                if currentInvScreenCell[0] < 0:
                                    currentInvScreenCell[0] = 0
                            if keys[pg.K_s] or keys[pg.K_DOWN]:
                                invMoveDelay += maxInvMoveDelay
                                currentInvScreenCell[1] -= 1
                                if currentInvScreenCell[1] < 0:
                                    currentInvScreenCell[1] = 0
                            if keys[pg.K_d] or keys[pg.K_RIGHT]:
                                invMoveDelay += maxInvMoveDelay
                                currentInvScreenCell[0] += 1
                                if currentInvScreenCell[0] > 4:
                                    currentInvScreenCell[0] = 4
                        if keys[pg.K_SPACE] and not prevKeyData[pg.K_SPACE] and invClickDelay <= 0:
                            invClickDelay += maxInvClickDelay
                            holdingCell = invHoldingItemstack.split(":")
                            hoveringCell = inv[int(currentInvScreenCell[0] +
                                               currentInvScreenCell[1]*5)].split(":")
                            # Shift, Alt, result
                            # FALSE FALSE If selected itemstack is same type or none, transfer all possible items; else, switch itemstacks.
                            # TRUE  FALSE Attempts to send selected itemstack to hotbar if not in hotbar, else to lowest spot available that is not in hotbar.
                            # FALSE  TRUE Transfer one item, if possible, to selected itemstack, if held itemstack is of same type. Else, if held itemstack is of a different type, switch itemstacks. If both are not true, pick up a half stack.
                            # TRUE   TRUE Attempts to send selected itemstack to hotbar if not in hotbar, else to lowest spot available that is not in hotbar.

                            # keys[pg.K_LSHIFT] and keys[pg.K_RSHIFT]:
                            if False:
                                pass
                            else:
                                if keys[pg.K_LALT] or keys[pg.K_RALT]:
                                    if hoveringCell[0] == holdingCell[0] or hoveringCell[0] == "0":
                                        if hoveringCell[1] != "64" and holdingCell[1] != "0":
                                            holdingCell[1] = str(
                                                int(holdingCell[1]) - 1)
                                            hoveringCell[1] = str(
                                                int(hoveringCell[1]) + 1)
                                            hoveringCell[0] = holdingCell[0]
                                            holdingCell[0] = "0" if holdingCell[1] == "0" else holdingCell[0]

                                else:
                                    if hoveringCell[0] == holdingCell[0] or hoveringCell[0] == "0":
                                        newHoldingCellValue = max(
                                            int(holdingCell[1]) - (64 - int(hoveringCell[1])), 0)
                                        newHoveringCellValue = min(
                                            int(hoveringCell[1]) + int(holdingCell[1]), 64)
                                        holdingCell[1] = str(
                                            newHoldingCellValue)
                                        hoveringCell[1] = str(
                                            newHoveringCellValue)
                                        hoveringCell[0] = holdingCell[0]
                                        holdingCell[0] = "0" if holdingCell[1] == "0" else holdingCell[0]
                                    else:
                                        holdingCell, hoveringCell = hoveringCell, holdingCell

                            hoveringCell, holdingCell = ":".join(
                                hoveringCell), ":".join(holdingCell)
                            invHoldingItemstack = holdingCell
                            inv[int(currentInvScreenCell[0] + currentInvScreenCell[1]
                                * 5)], inv[10] = hoveringCell, holdingCell
                            if SERVERMODE in "singleplayer,host":
                                setAttribute(
                                    index, 2, ";".join(inv))
                            else:
                                requests.post("http://" + host[0] + ".".join(
                                    list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 2 {';'.join(inv)}")

                    if keys[pg.K_e] and not prevKeyData[pg.K_e]:
                        invOpen = not invOpen
                        currentInvScreenCell = [currentInvCell, 0]
                    if not invOpen:
                        if pg.mouse.get_pressed()[0]:
                            block = ""
                            gridOffset = []
                            if newGrid[pos[1]][pos[0]] in "Dirt//Sand//Stone//Wood//Wood floor":
                                gridOffset = [0, 0]
                                block = newGrid[pos[1]][pos[0]]
                            elif playerDir == "Up" and newGrid[pos[1]-1][pos[0]] in "Dirt//Sand//Stone//Wood//Wood floor":
                                gridOffset = [-1, 0]
                                block = newGrid[pos[1]-1][pos[0]]
                            elif playerDir == "Left" and newGrid[pos[1]][pos[0]-1] in "Dirt//Sand//Stone//Wood//Wood floor":
                                gridOffset = [0, -1]
                                block = newGrid[pos[1]][pos[0]-1]
                            elif playerDir == "Down" and newGrid[pos[1]+1][pos[0]] in "Dirt//Sand//Stone//Wood//Wood floor":
                                gridOffset = [1, 0]
                                block = newGrid[pos[1]+1][pos[0]]
                            elif playerDir == "Right" and newGrid[pos[1]][pos[0]+1] in "Dirt//Sand//Stone//Wood//Wood floor":
                                gridOffset = [0, 1]
                                block = newGrid[pos[1]][pos[0]+1]
                            elif newGrid[pos[1]][pos[0]][:10] == "Wood door:":
                                gridOffset = [0, 0]
                                block = "Wood door"
                            elif playerDir == "Up" and newGrid[pos[1]-1][pos[0]][:10] == "Wood door:":
                                gridOffset = [-1, 0]
                                block = "Wood door"
                            elif playerDir == "Left" and newGrid[pos[1]][pos[0]-1][:10] == "Wood door:":
                                gridOffset = [0, -1]
                                block = "Wood door"
                            elif playerDir == "Down" and newGrid[pos[1]+1][pos[0]][:10] == "Wood door:":
                                gridOffset = [1, 0]
                                block = "Wood door"
                            elif playerDir == "Right" and newGrid[pos[1]][pos[0]+1][:10] == "Wood door:":
                                gridOffset = [0, 1]
                                block = "Wood door"

                            if block != "":
                                item = allItems.index(block) + 1
                                freeInvSlots = list(filter(lambda itemx: (int(itemx[1].split(":")[0]) == item and int(itemx[1].split(
                                    ":")[1]) < 64) or int(itemx[1].split(":")[0]) == 0, enumerate(inv)))
                                if len(freeInvSlots) > 0:
                                    if SERVERMODE in "singleplayer,host":
                                        setBlock(pos[0]+gridOffset[1],
                                                 pos[1]+gridOffset[0], "Grass")
                                    else:
                                        requests.post("http://" + host[0] + ".".join(list(
                                            host[1:5])) + host[5] + ":" + port + "/", f"grid {pos[0]+gridOffset[1]} {pos[1]+gridOffset[0]} Grass")
                                    invSlot = freeInvSlots[0][0]
                                    newInvSlot = inv[invSlot].split(":")
                                    newInvSlot[0] = item
                                    newInvSlot[1] = str(int(newInvSlot[1]) + 1)
                                    newInvSlot = str(newInvSlot[0]) + \
                                        ":" + str(newInvSlot[1])
                                    inv[invSlot] = newInvSlot
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(index, 2, ";".join(inv))
                                    else:
                                        requests.post("http://" + host[0] + ".".join(
                                            list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 2 {';'.join(inv)}")

                        if pg.mouse.get_pressed()[2]:
                            if not prevClickData[2]:
                                savedRotation = playerDir
                                if clickDelay <= 0:
                                    clickDelay += maxClickDelay
                                    if newGrid[pos[1]][pos[0]][:10] == "Wood door:":
                                        if SERVERMODE in "singleplayer,host":
                                            setBlock(pos[0], pos[1], newGrid[pos[1]][pos[0]][:11] +
                                                     ("c" if "o" == newGrid[pos[1]][pos[0]][11:12] else "o"))
                                        else:
                                            requests.post("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/",
                                                          f'grid {pos[0]} {pos[1]} {newGrid[pos[1]][pos[0]][:11] + ("c" if "o" == newGrid[pos[1]][pos[0]][11:12] else "o")}')
                                    elif playerDir == "Up" and newGrid[pos[1]-1][pos[0]][:10] == "Wood door:":
                                        if SERVERMODE in "singleplayer,host":
                                            setBlock(pos[0], pos[1]-1, newGrid[pos[1]-1][pos[0]][:11] +
                                                     ("c" if "o" == newGrid[pos[1]-1][pos[0]][11:12] else "o"))
                                        else:
                                            requests.post("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/",
                                                          f'grid {pos[0]} {pos[1]-1} {newGrid[pos[1]-1][pos[0]][:11] + ("c" if "o" == newGrid[pos[1]-1][pos[0]][11:12] else "o")}')
                                    elif playerDir == "Left" and newGrid[pos[1]][pos[0]-1][:10] == "Wood door:":
                                        if SERVERMODE in "singleplayer,host":
                                            setBlock(pos[0]-1, pos[1], newGrid[pos[1]][pos[0]-1][:11] +
                                                     ("c" if "o" == newGrid[pos[1]][pos[0]-1][11:12] else "o"))
                                        else:
                                            requests.post("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/",
                                                          f'grid {pos[0]-1} {pos[1]} {newGrid[pos[1]][pos[0]-1][:11] + ("c" if "o" == newGrid[pos[1][pos[0]-1]][11:12] else "o")}')
                                    elif playerDir == "Down" and newGrid[pos[1]+1][pos[0]][:10] == "Wood door:":
                                        if SERVERMODE in "singleplayer,host":
                                            setBlock(pos[0], pos[1]+1, newGrid[pos[1]+1][pos[0]][:11] +
                                                     ("c" if "o" == newGrid[pos[1]+1][pos[0]][11:12] else "o"))
                                        else:
                                            requests.post("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/",
                                                          f'grid {pos[0]} {pos[1]+1} {newGrid[pos[1]+1][pos[0]][:11] + ("c" if "o" == newGrid[pos[1]+1][pos[0]][11:12] else "o")}')
                                    elif playerDir == "Right" and newGrid[pos[1]][pos[0]+1][:10] == "Wood door:":
                                        if SERVERMODE in "singleplayer,host":
                                            setBlock(pos[0]+1, pos[1], newGrid[pos[1]][pos[0]+1][:11] +
                                                     ("c" if "o" == newGrid[pos[1]][pos[0]+1][11:12] else "o"))
                                        else:
                                            requests.post("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/",
                                                          f'grid {pos[0]+1} {pos[1]} {newGrid[pos[1]][pos[0]+1][:11] + ("c" if "o" == newGrid[pos[1][pos[0]+1]][11:12] else "o")}')
                            else:
                                if SERVERMODE in "singleplayer,host":
                                    setAttribute(index, 5, savedRotation)
                                else:
                                    requests.post("http://" + host[0] + ".".join(
                                        list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 5 {savedRotation}")
                                playerDir = savedRotation

                            if clickDelay <= 0:
                                clickDelay += maxClickDelay
                                newInvSlot = inv[int(
                                    currentInvCell)].split(":")
                                placeSucceeded = False
                                if newInvSlot[1] != "0":
                                    if newInvSlot[0] in "5":
                                        if ((playerDir == "Up" and newGrid[pos[1]-1][pos[0]][:10] != "Grass")
                                                or (playerDir == "Left" and newGrid[pos[1]][pos[0]-1][:10] != "Grass")
                                                or (playerDir == "Down" and newGrid[pos[1]+1][pos[0]][:10] != "Grass")
                                                or (playerDir == "Right" and newGrid[pos[1]][pos[0]+1][:10] != "Grass")) \
                                                and newGrid[pos[1]][pos[0]][:10] == "Grass":
                                            placeSucceeded = True
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(pos[0], pos[1],
                                                         allItems[int(newInvSlot[0]) - 1])
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]} {pos[1]} {allItems[int(newInvSlot[0]) - 1]}')
                                    if newInvSlot[0] in "12356":
                                        if playerDir == "Up" and newGrid[pos[1]-1][pos[0]][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(pos[0], pos[1]-1,
                                                         allItems[int(newInvSlot[0]) - 1])
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]} {pos[1]-1} {allItems[int(newInvSlot[0]) - 1]}')
                                            placeSucceeded = True
                                        elif playerDir == "Left" and newGrid[pos[1]][pos[0]-1][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(pos[0]-1, pos[1],
                                                         allItems[int(newInvSlot[0]) - 1])
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]-1} {pos[1]} {allItems[int(newInvSlot[0]) - 1]}')
                                            placeSucceeded = True
                                        elif playerDir == "Down" and newGrid[pos[1]+1][pos[0]][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(pos[0], pos[1]+1,
                                                         allItems[int(newInvSlot[0]) - 1])
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]} {pos[1]+1} {allItems[int(newInvSlot[0]) - 1]}')
                                            placeSucceeded = True
                                        elif playerDir == "Right" and newGrid[pos[1]][pos[0]+1][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(pos[0]+1, pos[1],
                                                         allItems[int(newInvSlot[0]) - 1])
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]+1} {pos[1]} {allItems[int(newInvSlot[0]) - 1]}')
                                            placeSucceeded = True
                                    elif newInvSlot[0] in "4":
                                        if playerDir == "Up" and newGrid[pos[1]-1][pos[0]][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(
                                                    pos[0], pos[1]-1, allItems[int(newInvSlot[0]) - 1] + ":sc")
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]} {pos[1]-1} {allItems[int(newInvSlot[0]) - 1] + ":sc"}')
                                            placeSucceeded = True
                                        elif playerDir == "Left" and newGrid[pos[1]][pos[0]-1][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(
                                                    pos[0]-1, pos[1], allItems[int(newInvSlot[0]) - 1] + ":ec")
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]-1} {pos[1]} {allItems[int(newInvSlot[0]) - 1] + ":ec"}')
                                            placeSucceeded = True
                                        elif playerDir == "Down" and newGrid[pos[1]+1][pos[0]][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(
                                                    pos[0], pos[1]+1, allItems[int(newInvSlot[0]) - 1] + ":nc")
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]} {pos[1]+1} {allItems[int(newInvSlot[0]) - 1] + ":nc"}')
                                            placeSucceeded = True
                                        elif playerDir == "Right" and newGrid[pos[1]][pos[0]+1][:10] == "Grass":
                                            if SERVERMODE in "singleplayer,host":
                                                setBlock(
                                                    pos[0]+1, pos[1], allItems[int(newInvSlot[0]) - 1] + ":wc")
                                            else:
                                                requests.post("http://" + host[0] + ".".join(list(
                                                    host[1:5])) + host[5] + ":" + port + "/", f'grid {pos[0]+1} {pos[1]} {allItems[int(newInvSlot[0]) - 1] + ":wc"}')
                                            placeSucceeded = True
                                if placeSucceeded:
                                    newInvSlot[1] = str(int(newInvSlot[1]) - 1)
                                    if newInvSlot[1] == "0":
                                        newInvSlot[0] = "0"
                                    newInvSlot = newInvSlot[0] + \
                                        ":" + newInvSlot[1]
                                    inv[int(currentInvCell)] = newInvSlot
                                    if SERVERMODE in "singleplayer,host":
                                        setAttribute(index, 2, ";".join(inv))
                                    else:
                                        requests.post("http://" + host[0] + ".".join(
                                            list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 2 {';'.join(inv)}")

                        else:
                            savedRotation = None

                    prevClickData = pg.mouse.get_pressed()
                    prevKeyData = pg.key.get_pressed()
                    playerPrevPositions = ",,,".join(locations).split(",,,")
                else:
                    textToLog = f'There is no player of name "{name}"!'

                if SERVERMODE != "singleplayer":
                    for i in range(len(players)):
                        if time_ns() - int(lastActions[i]) <= 5000000000 or i == index:
                            location = locations[i].split(":")
                            topOffset = -1/maxPlayerAnim * playerAnims[i]
                            leftOffset = -1/maxPlayerAnim * playerAnims[i]
                            topOffset *= int(mostRecentPlayerPositions[i].split(":")[
                                1]) - int(location[1])
                            leftOffset *= int(mostRecentPlayerPositions[i].split(":")[
                                0]) - int(location[0])

                            if cellSize*(int(location[0])+1 - leftOffset)+screenPos[0] >= 0 and cellSize*(int(location[0]) - leftOffset)+screenPos[0] <= pg.display.get_window_size()[0] and cellSize*(int(location[1])+1 - topOffset)+screenPos[1] >= 0 and cellSize*(int(location[1]) - topOffset)+screenPos[1] <= pg.display.get_window_size()[1]:
                                drawImage(allPlayerImages[indexOfPlayerImage(colors[i], directions[i])]["data"], (cellSize*(int(
                                    location[0]) + 0.05 - leftOffset)+screenPos[0], cellSize*(int(location[1]) + 0.05 - topOffset)+screenPos[1]), (cellSize*0.9, cellSize*0.9))
                    for i in range(len(players)):
                        if time_ns() - int(lastActions[i]) <= 5000000000 or i == index:
                            location = locations[i].split(":")
                            topOffset = -1/maxPlayerAnim * playerAnims[i]
                            leftOffset = -1/maxPlayerAnim * playerAnims[i]
                            topOffset *= int(mostRecentPlayerPositions[i].split(":")[
                                1]) - int(location[1])
                            leftOffset *= int(mostRecentPlayerPositions[i].split(":")[
                                0]) - int(location[0])
                            if cellSize*(int(location[0])+1 - leftOffset)+screenPos[0] >= 0 and cellSize*(int(location[0]) - leftOffset)+screenPos[0] <= pg.display.get_window_size()[0] and cellSize*(int(location[1])+1 - topOffset)+screenPos[1] >= 0 and cellSize*(int(location[1]) - topOffset)+screenPos[1] <= pg.display.get_window_size()[1]:
                                font = pg.font.Font(None, int(cellSize*0.25))
                                txt_surface = font.render(
                                    players[i], True, "white")
                                width = txt_surface.get_width()
                                screen.blit(txt_surface, ((cellSize*(int(
                                    location[0]) - leftOffset + 0.5)+screenPos[0]) - (width)/2, -cellSize*0.2 + cellSize*(int(location[1]) - topOffset)+screenPos[1]))
                else:
                    if name in players:
                        location = locations[index].split(":")
                        topOffset = -1/maxPlayerAnim * playerAnims[index]
                        leftOffset = -1/maxPlayerAnim * playerAnims[index]
                        topOffset *= int(mostRecentPlayerPositions[index].split(":")[
                            1]) - int(location[1])
                        leftOffset *= int(mostRecentPlayerPositions[index].split(":")[
                            0]) - int(location[0])

                        if cellSize*(int(location[0])+1 - leftOffset)+screenPos[0] >= 0 and cellSize*(int(location[0]) - leftOffset)+screenPos[0] <= pg.display.get_window_size()[0] and cellSize*(int(location[1])+1 - topOffset)+screenPos[1] >= 0 and cellSize*(int(location[1]) - topOffset)+screenPos[1] <= pg.display.get_window_size()[1]:
                            drawImage(allPlayerImages[indexOfPlayerImage(colors[index], directions[index])]["data"], (cellSize*(int(
                                location[0]) + 0.05 - leftOffset)+screenPos[0], cellSize*(int(location[1]) + 0.05 - topOffset)+screenPos[1]), (cellSize*0.9, cellSize*0.9))

                size = pg.display.get_window_size()
                if name in players:
                    drawImage(allUiImages[0]["data"], ((
                        size[0] - invBarWidth)/2, size[1] - invBarBottomOffset - 0.5*invBarHeight), (invBarWidth, invBarHeight), False)
                    if invOpen:
                        drawImage(allUiImages[0]["data"], ((
                            size[0] - invBarWidth)/2, size[1] - invBarBottomOffset - 1.45*invBarHeight), (invBarWidth, invBarHeight), False)
                    maxX = 2 if invOpen else 1
                    for x in range(maxX):
                        for i in range(5):
                            if inv[i + 5*x].split(":")[0] != "0":
                                drawImage(allInvImages[int(inv[i + 5*x].split(":")[0])-1]["data"], ((size[0] - invBarWidth)/2 + (1.05*i + 0.05) *
                                                                                                    invCellSize, size[1] - invBarBottomOffset - 0.5*invBarHeight + (0.05 - 1.05*x)*invCellSize), (invCellSize, invCellSize))
                                if inv[i + 5*x].split(":")[1] != "1":
                                    shadowOffsetX = 0.02
                                    shadowOffsetY = 0.02
                                    xOffsetMain = 0.8
                                    xOffsetShadow = xOffsetMain + shadowOffsetX
                                    yOffsetMain = 0.73
                                    yOffsetShadow = yOffsetMain + shadowOffsetY
                                    if len(inv[i + 5*x].split(":")[1]) > 1:
                                        xOffsetMain -= 0.15
                                        xOffsetShadow -= 0.15
                                    drawText(inv[i + 5*x].split(":")[1], numberFont, 0.4*invCellSize, ((size[0] - invBarWidth)/2 + (1.05*i + xOffsetShadow) * invCellSize, size[1] -
                                                                                                       invBarBottomOffset - 0.5*invBarHeight + (yOffsetShadow - 1.05*x)*invCellSize), pg.Color(0, 0, 0, 64), saveArray=numberImages)
                                    drawText(inv[i + 5*x].split(":")[1], numberFont, 0.4*invCellSize, ((size[0] - invBarWidth)/2 + (1.05*i + xOffsetMain) * invCellSize, size[1] -
                                                                                                       invBarBottomOffset - 0.5*invBarHeight + (yOffsetMain - 1.05*x)*invCellSize), "grey", saveArray=numberImages)
                    if invOpen:
                        pg.draw.rect(screen, "lightBlue", ((size[0] - invBarWidth)/2 + (1.05*currentInvScreenCell[0] + 0.05) * invCellSize, size[1] -
                                                           invBarBottomOffset - 0.5*invBarHeight + (0.05 - 1.05*currentInvScreenCell[1])*invCellSize, invCellSize, invCellSize), round(0.05*invCellSize))
                        if invHoldingItemstack != "0:0":
                            drawImage(allInvImages[int(invHoldingItemstack.split(":")[0])-1]["data"], ((size[0] - invBarWidth)/2 + (1.05*currentInvScreenCell[0] + 0.30) *
                                                                                                       invCellSize, size[1] - invBarBottomOffset - 0.5*invBarHeight + (0.30 - 1.05*currentInvScreenCell[1])*invCellSize), (invCellSize, invCellSize))
                            drawText(invHoldingItemstack.split(":")[1], numberFont, 0.4*invCellSize, ((size[0] - invBarWidth)/2 + (1.05*currentInvScreenCell[0] + 0.82 + 0.25 - (0.15 if len(invHoldingItemstack.split(":")[1]) > 1 else 0)) * invCellSize,
                                                                                                      size[1] - invBarBottomOffset - 0.5*invBarHeight + (0.25 + 0.75 - 1.05*currentInvScreenCell[1])*invCellSize), pg.Color(0, 0, 0, 64), saveArray=numberImages)
                            drawText(invHoldingItemstack.split(":")[1], numberFont, 0.4*invCellSize, ((size[0] - invBarWidth)/2 + (1.05*currentInvScreenCell[0] + 0.8 + 0.25 - (0.15 if len(invHoldingItemstack.split(":")[1]) > 1 else 0)) *
                                                                                                      invCellSize, size[1] - invBarBottomOffset - 0.5*invBarHeight + (0.25 + 0.73 - 1.05*currentInvScreenCell[1])*invCellSize), "grey", saveArray=numberImages)
                    else:
                        pg.draw.rect(screen, "lightBlue", ((size[0] - invBarWidth)/2 + (1.05*currentInvCell + 0.05) * invCellSize, size[1] -
                                                           invBarBottomOffset - 0.5*invBarHeight + 0.05*invCellSize, invCellSize, invCellSize), round(0.05*invCellSize))

                if showLog:
                    drawText(f"{data}\n{textToLog}", None,
                             25, (0, 0), (100, 100, 100), 0)

                if keys[pg.K_ESCAPE]:
                    mainMenu = True
                    if server_running:
                        server.shutdown()
                        server_running = False
                    if SERVERMODE == "join":
                        requests.post("http://" + host[0] + ".".join(
                            list(host[1:5])) + host[5] + ":" + port + "/", f"attr {index} 3 0")
                    else:
                        setAttribute(index, 3, "0")
                if keys[pg.K_f]:
                    pg.display.toggle_fullscreen()

                # drawText(players, None, 25, (0, 0), (100, 100, 100))
                # drawText(locations, None, 25, (0, 25), (100, 100, 100))
                # drawText(inventories, None, 25, (0, 50), (100, 100, 100))
                # drawText(lastActions, None, 25, (0, 75), (100, 100, 100))
                # drawText(newGrid, None, 25, (0, 100), (100, 100, 100))
                # drawText(textToLog, None, 25, (0, 150), (100, 100, 100))
                pg.display.flip()
            else:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        running = False
                        if server_running:
                            server.shutdown()
                            server_running = False
                    if event.type == pg.MOUSEBUTTONDOWN:
                        prevServerMode = SERVERMODE
                        button = pg.Rect(
                            (size[0] + 200)/2, (size[1]-160)/2, 60, 60)
                        if button.collidepoint(event.pos):
                            SERVERMODE = "singleplayer"
                            if prevServerMode != SERVERMODE:
                                host, port = "", ""
                        button.top += 65
                        if button.collidepoint(event.pos):
                            SERVERMODE = "join"
                            if prevServerMode != SERVERMODE:
                                host, port = "", ""
                        button.top += 65
                        if button.collidepoint(event.pos):
                            SERVERMODE = "host"
                            if prevServerMode != SERVERMODE:
                                host, port = "", ""
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            running = False
                        elif event.key == pg.K_UP:
                            if SERVERMODE == "join":
                                if len(port) == 0 and len(host) > 0:
                                    host = host[:-1] + \
                                        str((int(host[-1]) + 1) % 10)
                                elif len(port) > 0:
                                    port = port[:-1] + \
                                        str((int(port[-1]) + 1) % 10)
                            elif SERVERMODE == "host":
                                if len(port) > 0:
                                    port = port[:-1] + \
                                        str((int(port[-1]) + 1) % 10)
                        elif event.key == pg.K_DOWN:
                            if SERVERMODE == "join":
                                if len(port) == 0 and len(host) > 0:
                                    host = host[:-1] + \
                                        str((int(host[-1]) - 1) % 10)
                                elif len(port) > 0:
                                    port = port[:-1] + \
                                        str((int(port[-1]) - 1) % 10)
                            elif SERVERMODE == "host":
                                if len(port) > 0:
                                    port = port[:-1] + \
                                        str((int(port[-1]) - 1) % 10)
                        elif event.key == pg.K_LEFT:
                            if SERVERMODE == "join":
                                if len(port) == 0 and len(host) > 0:
                                    host = host[:-1]
                                elif len(port) > 0:
                                    port = port[:-1]
                            elif SERVERMODE == "host":
                                if len(port) > 0:
                                    port = port[:-1]
                        elif event.key == pg.K_RIGHT:
                            if SERVERMODE == "join":
                                if len(port) == 0 and len(host) < 6:
                                    host += "0"
                                elif len(port) < 4 and len(host) == 6:
                                    port += "0"
                            elif SERVERMODE == "host":
                                if len(port) < 4:
                                    port += "0"
                        elif event.key == pg.K_RETURN:
                            if SERVERMODE == "singleplayer" \
                                    or (SERVERMODE == "join" and len(host) == 6 and len(port) == 4) \
                                    or (SERVERMODE == "host" and len(port) == 4):
                                mainMenu = False
                                paused = False
                                invOpen = False
                                if SERVERMODE == "host":
                                    server = HTTPServer((socket.gethostbyname(
                                        socket.gethostname()), int(port)), HTTPRequestHandler)
                                    threading.Thread(
                                        target=server.serve_forever).start()
                                    server_running = True
                                if SERVERMODE == "singleplayer" or SERVERMODE == "host":
                                    lines = save.read_text().split("\n")
                                    if name not in lines[0][9:].split(", "):
                                        defaultAtributes = lines[6][20:].split(
                                            ", ")
                                        if len(lines[0].split(": ")[1]) == 0:
                                            # Username
                                            lines[0] += name
                                            # Location
                                            lines[1] += defaultAtributes[0]
                                            # Inventory
                                            lines[2] += defaultAtributes[1]
                                            # Last signal
                                            lines[3] += defaultAtributes[2]
                                            # Color
                                            lines[4] += preferredColor
                                            # Direction
                                            lines[5] += defaultAtributes[3]
                                        else:
                                            # Username
                                            lines[0] += ", " + \
                                                name
                                            # Location
                                            lines[1] += ", " + \
                                                defaultAtributes[0]
                                            # Inventory
                                            lines[2] += ", " + \
                                                defaultAtributes[1]
                                            # Last signal
                                            lines[3] += ", " + \
                                                defaultAtributes[2]
                                            # Color
                                            lines[4] += ", " + \
                                                preferredColor
                                            # Direction
                                            lines[5] += ", " + \
                                                defaultAtributes[3]
                                        save.write_text("\n".join(lines))
                                elif SERVERMODE == "join":
                                    if "0" in requests.get("http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/", f"joinPlayerTest {name}").text:
                                        requests.post(
                                            "http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/", f"joinPlayer {name} {preferredColor}")

                screen.fill("black")
                pg.draw.circle(screen, "white",
                               ((size[0] + 260)/2, (size[1]-130)/2), 30, 5)
                pg.draw.circle(screen, "white",
                               ((size[0] + 260)/2, size[1]/2), 30, 5)
                pg.draw.circle(screen, "white",
                               ((size[0] + 260)/2, (size[1]+130)/2), 30, 5)
                drawText("Singleplayer", None, 50,
                         ((size[0] - 250)/2, (size[1]-170)/2), "white")
                offset = -500 if SERVERMODE == "join" else 0
                string = "["
                string += "_" if len(host) == 0 else host[0]
                string += ("_" if len(host) <= 1 else host[1]) + "."
                string += ("_" if len(host) <= 2 else host[2]) + "."
                string += ("_" if len(host) <= 3 else host[3]) + "."
                string += "_" if len(host) <= 4 else host[4]
                string += ("_" if len(host) <= 5 else host[5]) + ":"
                string += port
                string += "_" * (4 - len(port)) + "]"
                drawText("Join" + (string if SERVERMODE == "join" else ""), None, 50,
                         ((size[0] + 35 + offset)/2, (size[1]-40)/2), "white")
                offset = -545 if SERVERMODE == "host" else 0
                drawText("Host" + (f": {socket.gethostbyname(socket.gethostname())}:[{port + ('_' * (4 - len(port)))}]" if SERVERMODE == "host" else ""), None, 50,
                         ((size[0] + 25 + offset)/2, (size[1]+90)/2), "white")

                offset = 130 * (0 if SERVERMODE == "singleplayer" else (
                    1 if SERVERMODE == "join" else (2 if SERVERMODE == "host" else -1)))
                if SERVERMODE != "none":
                    pg.draw.circle(
                        screen, "white", ((size[0] + 260)/2, (size[1]-130 + offset)/2), 20)

                pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    if server_running:
                        server.shutdown()
                        server_running = False
            dt = clock.tick(30)/1000
        # except Exception as error:
        #     drawText(error, None, 50, (0, 0), (255, 0, 0), 0)
        pg.quit()

    run()
except BaseException as error:
    if runningInEditor:
        if server_running:
            server.shutdown()
        raise error
    else:
        Path("errorLog.txt").write_text(Path("errorLog.txt").read_text() +
                                        "\n" + datetime.now().strftime("%Y, %m, %d at %H:%M:%S.%f") + ":  " + str(error))
if server_running:
    server.shutdown()
