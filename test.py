import requests
host = "100081"
port = "9999"
print(requests.get(
    "http://" + host[0] + ".".join(list(host[1:5])) + host[5] + ":" + port + "/").text)
