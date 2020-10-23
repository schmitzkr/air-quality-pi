from sds011 import *
sensor = SDS011("/dev/ttyUSB0")

pmt_2_5, pmt_10 = sensor.query()