import serial
from serial.tools import list_ports
import contextlib
import os

DRIVER_ACK = b'ok\r\nok\r\n'
RECOVERY_TIMEOUT = 10
DEFAULT_SERIAL_TIMEOUT = 5
DEFAULT_WRITE_TIMEOUT = 30

SMOOTHIE_PORT_ID = 'COM5'

#if os.environ.get('RUNNING_ON_PI'):
#SMOOTHIE_PORT_ID = 'AMA'

ERROR_KEYWORD = b'error'
ALARM_KEYWORD = b'ALARM'

BAUDRATE = 115200


def get_ports(device_name):
    '''Returns all serial devices with a given name'''
    filtered_devices = filter(
        lambda device: device_name in device[1],
        list_ports.comports()
    )
    device_ports = [device[0] for device in filtered_devices]
    return device_ports


@contextlib.contextmanager
def serial_with_temp_timeout(serial_connection, timeout):
    '''Implements a temporary timeout for a serial connection'''
    saved_timeout = serial_connection.timeout
    if timeout is not None:
        serial_connection.timeout = timeout
    yield serial_connection
    serial_connection.timeout = saved_timeout


def _parse_smoothie_response(response):
    if ERROR_KEYWORD in response or ALARM_KEYWORD in response:
        print("[SMOOTHIE ISSUE]: ", response)

    if DRIVER_ACK in response:
        parsed_response = response.split(DRIVER_ACK)[0]
        return parsed_response
    else:
        return None


def clear_buffer(serial_connection):
    serial_connection.reset_input_buffer()


def _write_to_device_and_return(cmd, device_connection):
    '''Writes to a serial device.
    - Formats command
    - Wait for ack return
    - return parsed response'''
    command = cmd + '\r\n'
    device_connection.write(command.encode())

    response = device_connection.read_until(DRIVER_ACK)

    clean_response = _parse_smoothie_response(response)
    if clean_response:
        clean_response = clean_response.decode()
    return clean_response


def _connect(port_name, baudrate):
    return serial.Serial(
        port=port_name,
        baudrate=baudrate,
        timeout=DEFAULT_SERIAL_TIMEOUT
    )

def write_and_return(
        command, serial_connection, timeout=DEFAULT_WRITE_TIMEOUT):
    '''Write a command and return the response'''
    clear_buffer(serial_connection)
    with serial_with_temp_timeout(
            serial_connection, timeout) as device_connection:
        response = _write_to_device_and_return(command, device_connection)
    return response


def connect(device_name=SMOOTHIE_PORT_ID):
    '''
    Creates a serial connection
    :param device_name: defaults to 'Smoothieboard'
    :return: serial.Serial connection
    '''
    smoothie_port = get_ports(device_name=device_name)[0]
    return _connect(port_name=smoothie_port, baudrate=BAUDRATE)