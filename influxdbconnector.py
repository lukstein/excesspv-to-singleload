# import settings
from influxlogin import *

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

client = influxdb_client.InfluxDBClient(
    url=url,
    token=token,
    org=org
)

# Write script
write_api = client.write_api(write_options=SYNCHRONOUS)

def write_point(measurement: str, tag: tuple, value: tuple):
    """
    measurement: name of measurement. for example boiler
    """
    p = influxdb_client.Point(measurement).tag(tag[0], tag[1]).field(value[0], value[1])
    write_api.write(bucket=bucket, org=org, record=p)
