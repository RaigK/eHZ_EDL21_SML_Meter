import logging

from pycli_tools.commands import Command, arg
from pycli_tools.parsers import get_argparser
from serial.serialutil import SerialException

from eHZ_EDL21_SML_Meter import SMLMeter
from sml_meter_ehz import __version__

log = logging.getLogger(__name__)

#DEFAULT_SERIAL='/dev/ttyUSB0'
DEFAULT_SERIAL = 'COM4'


class ReadMeterCommand(Command):
    '''Read a single eHZ EDL21 packet
    '''

    args = [
        arg('--serial-port', default=DEFAULT_SERIAL, metavar=DEFAULT_SERIAL,
            help='serial port to read packets from (defaults to %s)' % DEFAULT_SERIAL),
        arg('--baudrate', default=9600,
            help='baudrate for the serial connection'),
        arg('--tsv', action='store_true',
            help='display packet in tab seperated value form'),
        arg('--raw', action='store_true',
            help='display packet in raw form'),
    ]

    def run(self, args, parser):
        meter = SMLMeter(args.serial_port,
                            baudrate=args.baudrate)

        try:
            packet = meter.read_one_packet()
        except SerialException as e:
            parser.error(e)
        finally:
            meter.disconnect()

        if args.raw:
            print(str(packet))
            return 0

        data = [
            ('Time', (packet['kWh']['time']['now'])),
            ('Time difference', (packet['kWh']['time']['dif'])),
            ('Total kWh 1.8.0  consumed', (packet['kWh']['1.8.0']['consumed'])),
            ('Total kWh 2.8.0 delivered', (packet['kWh']['2.8.0']['produced'])),
            ('Current power consumption', (packet['kWh']['15.7.0']['power']))
        ]

        if args.tsv:
            print('\t'.join(map(str, [d for k,d in data])))
        else:
            print('\n'.join(['%-25s %s' % (k,d) for k,d in data]))




def parse_and_run(args=None):
    parser = get_argparser(
        prog='sml_meter',
        version=__version__,
        logging_format='[%(asctime)-15s] %(levelname)s %(message)s',
        description='Read smart meter SML packets'
    )

    parser.add_commands([
        ReadMeterCommand(),
    ])

    args = parser.parse_args()
    args.func(args, parser=parser)
