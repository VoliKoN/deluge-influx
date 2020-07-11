import requests
import json
from influxdb import InfluxDBClient

URL = "http://INSERT_IP_HERE:8112/json"
WEB_PASSWORD = "INSERT_PASSWORD_HERE"
TORRENT_PARAMS = ['name', 'state', 'progress', 'num_seeds', 'total_seeds', 'num_peers', 'total_peers', 'download_payload_rate', 'upload_payload_rate', 'ratio', 'tracker_host', 'total_done', 'total_uploaded', 'label']
INFLUXDB_HOST = 'INSERT_IP_HERE'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PASS = 'root'
INFLUXDB_DB = 'deluge'

HEADERS = {
    'Content-Type': "application/json",
    'Accept': "application/json",
    }
try:
    auth_payload = {"id": 1, "method": "auth.login", "params": [WEB_PASSWORD]}
    response = requests.request("POST", URL, data=json.dumps(auth_payload), headers=HEADERS)
    assert json.loads(response.text)["result"] == True, "Wrong Password!"
    cookies = response.cookies
    payload_dict = {'method': 'web.update_ui', 'params': [TORRENT_PARAMS, {}], 'id': 2}
    response = requests.request("POST", URL, data=json.dumps(payload_dict), headers=HEADERS, cookies=cookies)

    response_json = json.loads(response.text)
    if response_json['error'] == None:
        stats = response_json['result']['stats']
        torrents = response_json['result']['torrents']
        influx_client = InfluxDBClient(INFLUXDB_HOST, INFLUXDB_PORT, INFLUXDB_USER, INFLUXDB_PASS, INFLUXDB_DB)
        json_body = []
        for torrent in torrents:
            torrent_params = torrents[torrent]
            point = {
            "measurement": "torrent",
            "tags": {
                "tracker_host": torrent_params.pop('tracker_host'),
                "name": torrent_params.pop('name'),
                "label": torrent_params.pop('label'),
                "hex": torrent
            },
            "fields": torrent_params
            }
            json_body.append(point)
        
        stats["torrents_count"] = len(json_body)
        point = {
        "measurement": "stats",
        "tags": {},
        "fields": stats
        }
        json_body.append(point)
        influx_client.write_points(json_body)
except Exception:
    raise
finally:
    payload = "{\n\t\"method\": \"auth.delete_session\",\n\t\"params\": [],\n    \"id\": 3\n}"
    response = requests.request("POST", URL, data=payload, headers=HEADERS, cookies=cookies)
