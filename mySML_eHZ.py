import sys

import xively

from sml_meter import SMLMeter
from my_xively_key import XIVELY_API_KEY

def main():
    api = xively.XivelyAPIClient(XIVELY_API_KEY)
    feed = api.feeds.get(77707)

    meter = SMLMeter('COM4')

    while True:
        packet = meter.read_one_packet()
        data = [
            ('Time', (packet['kWh']['time']['now'])),
            ('Time difference', (packet['kWh']['time']['dif'])),
            ('Total kWh 1.8.0  consumed', (packet['kWh']['1.8.0']['consumed'])),
            ('Total kWh 2.8.0 delivered', (packet['kWh']['2.8.0']['produced'])),
            ('Current power consumption', (packet['kWh']['15.7.0']['power']))
        ]

        print('\n'.join(['%-25s %s' % (k,d) for k,d in data]))
        try:
            power_value = (packet['kWh']['15.7.0']['power'])
            if power_value < 0:
                current_value_deliver = abs(power_value)
                current_value_receipt = 0
            else:
                current_value_receipt = power_value
                current_value_deliver = 0
            feed.datastreams = [
                xively.Datastream(id='Energy_Production', current_value=current_value_deliver),
                xively.Datastream(id='Energy_Consumtion', current_value=current_value_receipt)
            ]
            feed.update()
        except:
            print "feed update error"
        finally:
            pass

if __name__ == '__main__':
    try:
        args = sys.argv[1:]
        main(*args)
    except KeyboardInterrupt:
        pass