import paho.mqtt.client as mqtt
import http.client as http
import json
import urllib
import logging
import base64
import uuid
import pprint

logging.basicConfig(level=logging.DEBUG)
logging.debug('This will get logged')


## Subscription registration

api_url = 'XXXX.appsync-api.us-east-1.amazonaws.com'
api_key = 'da2-XXXXXXXX'

conn = http.HTTPSConnection(api_url, 443)
headers = {'Content-type': 'application/json', 'x-api-key': api_key}
body = {"query":"\nsubscription events {\n\tsubscribeToEventComments(eventId:\"207e7c6c-60cc-4602-ac39-daeab036fe2d\") {\n    eventId\n    commentId\n  }\n}","variables":None,"operationName":"events"}
json_body = json.dumps(body)
conn.request('POST', '/graphql', json_body, headers)
response_json = conn.getresponse()
response = json.loads(response_json.read().decode())

print(response)
ws_endpoint_str = response['extensions']['subscription']['mqttConnections'][0]['url']
mqtt_topic = response['extensions']['subscription']['mqttConnections'][0]['topics'][0]
mqtt_client_id = response['extensions']['subscription']['mqttConnections'][0]['client']
ws_endpoint = urllib.parse.urlparse(ws_endpoint_str)
print(ws_endpoint)
# print(ws_endpoint.query)

ws_domain = ws_endpoint.netloc
ws_path = ws_endpoint.path
# dictionary representing the query arguments
ws_query_args = dict(urllib.parse.parse_qsl(ws_endpoint.query))

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(ws_query_args)

## Subscription connection

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(mqtt_topic, qos=1)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_log(client, userdata, level, buf):
    print("log: ",buf)    

client = mqtt.Client(client_id=mqtt_client_id, clean_session= True, transport="websockets", protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message
client.on_log = on_log
client.enable_logger(logger=logging)

client.ws_set_options(path=ws_path + "?" + ws_endpoint.query)
client.tls_set()
client.connect(ws_domain, 443)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

print("looping...")
client.loop_forever()

# {
#     "extensions": {
#         "subscription": {
#             "mqttConnections": [
#                 {
#                     "url": "wss://xxxxxx-ats.iot.us-east-1.amazonaws.com/mqtt?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAS3UEXNWQ7NXA2YMQ%2F20190124%2Fus-east-1%2Fiotdevicegateway%2Faws4_request&X-Amz-Date=20190124T204605Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host&X-Amz-Signature=d9ee2b90f4132167129fc011f70843e959bb97a5e4a8a9c46e24e4f00bfb2c7e&X-Amz-Security-Token=AgoGb3JpZ2luEOn%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCXVzLWVhc3QtMSKAAkh3qWZQ9jPH%2FbPCa8L2LgO8W6F5DaQ6MH7GUTjfe87nnVY17OzmqssjzmAIuQIZgFIdEYOCOv6hwI1iVstGNJAGnutPsB8oUILlXvdx%2BtvMPJHFTjENe%2BxyfKIHinw3qu7KTvpZv26NjG69qe5g%2BdsV9Yw4ulT5ObzMEXKPqKvRJyKEGtUvRfLKJHiEApRJvTWV9q48wv8KqP57tl91f%2FCThEvaY4VhtHjFHxVEUUXBuRIZ1VRCrRhnJh29i80RXBYpafDvyKIHLkxgIvcGOUw%2BnPpYvOKgOkV9wkgAm1XLaN%2FRSL3A7nY43v0rSn3E67EmqDKJGbayvtt3UAuJfRsqjwQI3v%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARAAGgwxOTY3NzMxMTMyNDkiDFbs5ZT%2B6sbRpG3nqSrjA%2Bj9o4zgP5byUMeYP90mv8flkcBRBiCsO%2FFo1McxMLPMmytU48X2%2FEYFTmxE6TMnzf28Cg7J6LyXPEv5KQCtBYulfjciUmiJO07CcmFVW3x6dN%2FXvQo%2F8OrdbpWxe9j3LFaZRdOBPJBYMPNpOseSD5NoRX7d3lGaxHAJTCmznuu%2BUeUlhH8p7s3sClpp5WGz7tL05VvPinahR2laGdYLTeCOzDUF79vrkCMtnU4NLG2J7ODY1c1MlnXfIlkxoqx1V9juJPDxvo6NOAxrvYOJ5yBDSU%2FzgXcd9G3U4xCzUCtk5PKPpN4yJOROQfSP6eTydO1Oe%2Ffi8ItUMUdaCoddsV%2B3pOAG9UrttXZZ5BhycLpp0UBGXtmQ8TKoJYx85GwpN4mOC%2FaIHwQVRO6cP2Ctr8ufhrzXOwYXVxPkMSmvZALMxdNMyyOQYA0u7vJFh2wkex6%2F3WRV2t2HmN3QRpJze23e3LQyfmCQF4un50S4gPJUaaK9n%2Fd%2FeD1SxD9FqMo39yzc2ZAp7qwjNB4baLtCUVnwujB%2Fo6tZKFM%2Ff1egxiAzw3NVbkpsXpogcAXV4TK4U%2BuzcwfiAEuYmgXOMw47pwZfTyx0nDnRp4k5BJ4dJWHr9DONkfQ2GCJJLsnRhq6RGQpUszCNyKjiBQ%3D%3D",
#                     "topics": [
#                         "xxxxx/zzzzzzzzz/subscribeToEventComments/f075522877f069082095963a6d511bb365202e5561d49e2fe19176b93f9a09e0"
#                     ],
#                     "client": "jofnwahji5chnivwisu4uerqea"
#                 }
#             ],
#             "newSubscriptions": {
#                 "subscribeToEventComments": {
#                     "topic": "xxxxxxx/zzzzzz/subscribeToEventComments/f075522877f069082095963a6d511bb365202e5561d49e2fe19176b93f9a09e0",
#                     "expireTime": null
#                 }
#             }
#         }
#     },
#     "data": {
#         "subscribeToEventComments": null
#     }
# }