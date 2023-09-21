import json

import requests
import websocket


def on_message(ws, message):
    print("Received:")

    json_message = json.loads(message)

    if "Persistent" in json_message:
        json_message = json_message["Persistent"]

        if "value" in json_message:
            json_message = json_message["value"]
            try:
                temperature = json_message["temperature"]
                name = json_message["name"]
                data = {"name": name, "temperature": temperature}
                url = "http://localhost:6000/temperature"
                response = requests.post(url, json=data)
                print(name, temperature)
                if response.status_code == 200:
                    print("Data sent to Flask server")
                else:
                    print("Failed to send data to Flask server")
            except:
                pass


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### Connection closed ###")


def on_open(ws):
    print("### Connection established ###")


if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        "ws://localhost:3000/ws",
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()
