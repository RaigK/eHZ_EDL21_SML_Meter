import re
import logging
import serial
import binascii
from timestamp import TimeStamp
from ctypes import *

regCompleteMsg = re.compile(r'(1b1b1b1b01010101).*(1b1b1b1b1a)(.{8})')
regEoMsg = re.compile(r'(1b1b1b1b1a)')
reg15_7_0 = re.compile(r'(77070100100700ff)(0101621b)(52ff)..(.{8})')
reg1_8_0 = re.compile(r'(77070100010801ff).*?.52(.{2})....(.{8})')
reg2_8_0 = re.compile(r'(77070100020801ff).*?.52(.{2})....(.{8})')

log = logging.getLogger(__name__)
ts = TimeStamp()


class SMLMeter(object):

    def __init__(self, port, *args, **kwargs):
        try:
            self.serial = serial.Serial(
                port,
                kwargs.get('baudrate', 9600),
                timeout=10,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
        except (serial.SerialException,OSError) as e:
            raise SmartMeterError(e)
        else:
            self.serial.setRTS(False)
            self.port = self.serial.name

        log.info('New serial connection opened to %s', self.port)

    def connect(self):
        if not self.serial.isOpen():
            log.info('Opening connection to `%s`', self.serial.name)
            self.serial.open()
            self.serial.setRTS(False)
        else:
            log.debug('`%s` was already open.', self.serial.name)

    def disconnect(self):
        if self.serial.isOpen():
            log.info('Closing connection to `%s`.', self.serial.name)
            self.serial.close()
        else:
            log.debug('`%s` was already closed.', self.serial.name)

    def connected(self):
        return self.serial.isOpen()

    def read_one_packet(self):
        chunk = " "
        line = ''

        lines = []
        lines_read = 0
        complete_packet = False

        log.info('Start reading lines')

        while not complete_packet:
            try:
                #line = self.serial.readline().strip()
                chunk = self.serial.read()
                line += binascii.hexlify(chunk)
                for match in regCompleteMsg.finditer(line):
                    smldata = line
                    line=""
                    chunk=""
                    complete_packet = True
            except Exception as e:
                log.error(e)
                log.error('No data block read')
                raise SmartMeterError(e)
            finally:
                log.debug('>> %s', line)

        log.info('Done reading one packet (containing %d lines)' % len(lines))
        log.debug('Total lines read from serial port: %d', lines_read)
        log.debug('Constructing P1Packet from raw data')

        return SMLPacket(smldata)


class SmartMeterError(Exception):
    pass


class SMLPacket(object):
    _raw = ''
    time_old = None

    def __init__(self, data):
        if type(data) == list:
           self._raw = '\n'.join(data)
        else:
            self._raw = data

        ts.timestamp()
        keys = {}

        keys["kWh"] = {}
        keys["kWh"]["time"] = {}
        #keys["kWh"]["time"]["past"] = self.time_old
        keys["kWh"]["time"]["now"] = ts.time_now
        keys["kWh"]["time"]["dif"] = ts.time_dif

        keys["kWh"]["1.8.0"] = {}
        keys["kWh"]["1.8.0"]["consumed"] = (self.get(reg1_8_0, 3)) / 10000.0

        keys["kWh"]["2.8.0"] = {}
        keys["kWh"]["2.8.0"]["produced"] = (self.get(reg2_8_0, 3)) / 10000.0

        keys["kWh"]["15.7.0"] = {}
        keys["kWh"]["15.7.0"]["power"] = (self.get(reg15_7_0, 4)) / 10.0

        self._keys = keys

    def __getitem__(self, key):
        return self._keys[key]

    def get(self, regex, group, default=None):
        results = int (re.search(regex, self._raw).group(group),16)
        if(results & 0x80000000):
            results = -0x100000000 + results
        if not results:
            return default
        return results

    def __str__(self):
        return self._raw

