import paho.mqtt.client as mqtt

# Settings
broker = "test.mosquitto.org"
port = 1883
topic = "test/topic"

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic)

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

# Create a client instance
client = mqtt.Client()

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to broker
client.connect(broker, port, 60)

# Loop forever
client.loop_forever()

