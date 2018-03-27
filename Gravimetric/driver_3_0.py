import serial_communication
from os import environ

PLUNGER_CURRENT_HIGH = 0.5
PLUNGER_CURRENT_LOW = 0.1

DEFAULT_ACCELERATION = 'M204 S10000 X4000 Y3000 Z1500 A1500 B1000 C1000'
DEFAULT_CURRENT = 'M907 X1.2 Y1.5 Z0.8 A0.8 B{0} C{0}'.format(PLUNGER_CURRENT_LOW)
DEFAULT_MAX_SPEEDS = 'M203.1 X600 Y600 Z100 A100 B8 C8'
DEFAULT_STEPS_PER_MM = 'M92 X80.0254 Y80.16 Z400 A400 B768 C768'


HOMED_POSITION = {
    'X': 394,
    'Y': 344,
    'Z': 227,
    'A': 227,
    'B': 18.9997,
    'C': 18.9997
}

HOME_SEQUENCE = ['ZABC', 'X', 'Y']
AXES = ''.join(HOME_SEQUENCE)
DISABLED_AXES = ''
SEC_PER_MIN = 60

GCODES = {'HOME': 'G28.2',
          'MOVE': 'G0',
          'DWELL': 'G4',
          'CURRENT_POSITION': 'M114.2',
          'LIMIT_SWITCH_STATUS': 'M119',
          'PROBE': 'G38.2',
          'ABSOLUTE_COORDS': 'G90',
          'RESET_FROM_ERROR': 'M999',
          'SET_SPEED': 'G0F',
          'SET_CURRENT': 'M907',
          'Enable_Motors': 'M17',
          'Disable_Motors': 'M18'}


def _parse_axis_values(raw_axis_values):
    parsed_values = raw_axis_values.split(' ')
    parsed_values = parsed_values[2:]
    return {
        s.split(':')[0].upper(): float(s.split(':')[1])
        for s in parsed_values
    }


class SmoothieDriver_3_0_0:
    def __init__(self):
        self._position = {}
        self.log = []
        self._update_position({axis: 0 for axis in AXES})
        self.simulating = True
        self._connection = None

    def _update_position(self, target):
        self._position.update({
            axis: value
            for axis, value in target.items() if value is not None
        })

        self.log += [self._position.copy()]

    def update_position(self, default=None, is_retry=False):
        if default is None:
            default = self._position

        if self.simulating:
            updated_position = self._position.copy()
            updated_position.update(**default)

        if not self.simulating:
            try:
                position_response = \
                    self._send_command(GCODES['CURRENT_POSITION'])
                updated_position = \
                    _parse_axis_values(position_response)
                # TODO jmg 10/27: log warning rather than an exception
            except TypeError as e:
                if is_retry:
                    raise e
                else:
                    self.update_position(default=default, is_retry=True)

        self._update_position(updated_position)

    def connect(self):
        self.simulating = False
        if environ.get('ENABLE_VIRTUAL_SMOOTHIE', '').lower() == 'true':
            self.simulating = True
            return

        self._connection = serial_communication.connect()
        self._setup()

    def disconnect(self):
        self.simulating = True
    
    @property
    def position(self):
        return {k.upper(): v for k, v in self._position.items()}

    @property
    def switch_state(self):
        '''Returns the state of all SmoothieBoard limit switches'''
        return self._send_command(GCODES['LIMIT_SWITCH_STATUS'])

    def set_speed(self, value):
        ''' set total axes movement speed in mm/second'''
        self._combined_speed = float(value)
        speed_per_min = int(self._combined_speed * SEC_PER_MIN)
        command = GCODES['SET_SPEED'] + str(speed_per_min)
        self._send_command(command)
    
    def enable_motors(self):
        #Enable motors
        return self._send_command(GCODES['Enable_Motors'])
    
    def disable_motors(self):
        #Enable motors
        return self._send_command(GCODES['Disable_Motors'])
    
    def set_current(self, axes, value):
        ''' set total movement speed in mm/second'''
        values = ['{}{}'.format(axis, value) for axis in axes]
        command = '{} {}'.format(
            GCODES['SET_CURRENT'],
            ' '.join(values)
        )
        self._send_command(command)
        self.delay(0.05)

    # ----------- Private functions --------------- #

    def _reset_from_error(self):
        self._send_command(GCODES['RESET_FROM_ERROR'])

    # TODO: Write GPIO low
    def _reboot(self):
        self._setup()

    # Potential place for command optimization (buffering, flushing, etc)
    def _send_command(self, command, timeout=None):
        if self.simulating:
            pass
        else:
            moving_plunger = ('B' in command or 'C' in command) \
                and (GCODES['MOVE'] in command or GCODES['HOME'] in command)

            if moving_plunger:
                self.set_current('BC', PLUNGER_CURRENT_HIGH)

            command_line = command + ' M400'
            ret_code = serial_communication.write_and_return(
                command_line, self._connection, timeout)

            if moving_plunger:
                self.set_current('BC', PLUNGER_CURRENT_LOW)

            return ret_code

    def _setup(self):
        self._reset_from_error()
        self._send_command(DEFAULT_ACCELERATION)
        self._send_command(DEFAULT_CURRENT)
        self._send_command(DEFAULT_MAX_SPEEDS)
        self._send_command(DEFAULT_STEPS_PER_MM)
        self._send_command(GCODES['ABSOLUTE_COORDS'])
    # ----------- END Private functions ----------- #

    # ----------- Public interface ---------------- #
    def move(self, x=None, y=None, z=None, a=None, b=None, c=None, speed=None):
        from numpy import isclose
        target_position = {'X': x, 'Y': y, 'Z': z, 'A': a, 'B': b, 'C': c}

        #print("speed is ", speed)
        def valid_movement(coords, axis):
            return not (
                (axis in DISABLED_AXES) or
                (coords is None) or
                isclose(coords, self._position[axis])
            )

        coords = [axis + str(coords)
                  for axis, coords in target_position.items()
                  if valid_movement(coords, axis)]
        #speed is in mm/s
        movement_speed = ''
        if speed:
            movement_speed = 'F'+str(speed * 60)

        if coords:
            command = GCODES['MOVE'] + ''.join(coords) + movement_speed
            self._send_command(command)
            self._update_position(target_position)

    def home(self, axis=AXES, disabled=DISABLED_AXES):
        axis = axis.upper()

        # If Y is requested make sure we home X first
        if 'Y' in axis:
            axis += 'X'
        # If horizontal movement is requested, ensure we raise the instruments
        if 'X' in axis:
            axis += 'ZA'
        # These two additions are safe even if they duplicate requested axes
        # because of the use of set operations below, which will de-duplicate
        # characters from the resulting string

        # HOME_SEQUENCE defines a pattern for homing, specifically that the
        # ZABC axes should be homed first so that horizontal movement doesn't
        # happen with the pipette down (which could bump into things). Then
        # the X axis is homed, which has to happen before Y. Finally Y can be
        # homed. This variable will contain the sequence just explained, but
        # filters out unrequested axes using set intersection (&) and then
        # filters out disabled axes using set difference (-)
        home_sequence = list(filter(
            None,
            [
                ''.join(set(group) & set(axis) - set(disabled))
                for group in HOME_SEQUENCE
            ]))

        command = ' '.join([GCODES['HOME'] + axes for axes in home_sequence])
        self._send_command(command, timeout=30)

        position = HOMED_POSITION

        # if not self.simulating:
        #     position = _parse_axis_values(
        #         self._send_command(GCODES['CURRENT_POSITION'])
        #     )

        # Only update axes that have been selected for homing
        homed = {
            ax: position[ax]
            for ax in ''.join(home_sequence)
        }

        self.update_position(default=homed)

        return homed

    def delay(self, seconds):
        # per http://smoothieware.org/supported-g-codes:
        # In grbl mode P is float seconds to comply with gcode standards
        command = '{code}P{seconds}'.format(
            code=GCODES['DWELL'],
            seconds=seconds
        )
        self._send_command(command)

    def probe_axis(self, axis, probing_distance):
        if axis.upper() in AXES:
            command = GCODES['PROBE'] + axis.upper() + str(probing_distance)
            self._send_command(command=command, timeout=30)
            return self._position[axis.upper()]
        else:
            raise RuntimeError("Cant probe axis {}".format(axis))

    # TODO: Write GPIO low
    def kill(self):
        self_send_command('M999')
    
    

    # ----------- END Public interface ------------ #