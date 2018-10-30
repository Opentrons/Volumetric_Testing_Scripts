"""
@author opentrons
@date October 18, 2018
@version V1.1
@description Singlechannel Use
"""
from opentrons import labware, instruments, robot

"""
Customization fields
Adjust these fields as needed for volume testing
"""

# Choose the amount of plates you would like to run
num_plates = 1
pipette_type = 'p10_single'  # change based on pipette type (single only)
mount = 'right'  # 'left' or 'right' mount
dye_loc = 'A1'  # dye location in trough

# Change the volumes you are testing here
VOLUME_ONE = 10  # volume tested in plate 1
VOLUME_TWO = 9  # volume tested in plate 2
VOLUME_THREE = 8  # volume tested in plate 3
VOLUME_FOUR = 7  # volume tested in plate 4
VOLUME_FIVE = 6  # volume tested in plate 5
VOLUME_SIX = 5  # volume tested in plate 6

"""
Protocol setup
"""

# labware definitions
if pipette_type == 'p10_single':
    tip_type = 'tiprack-10ul'
else:
    tip_type = 'opentrons-tiprack-300ul'

tiprack1 = labware.load(tip_type, '6', 'Tiprack 1')
tiprack2 = labware.load(tip_type, '9', 'Tiprack 2')
tiprack3 = labware.load(tip_type, '10', 'Tiprack 3')
tiprack4 = labware.load(tip_type, '11', 'Tiprack 4')
dye_trough = labware.load('trough-12row', '3', 'Dye Trough')

plate_1 = labware.load('96-flat', '1')
plate_2 = labware.load('96-flat', '2')
plate_3 = labware.load('96-flat', '4')
plate_4 = labware.load('96-flat', '5')
plate_5 = labware.load('96-flat', '7')
plate_6 = labware.load('96-flat', '8')

"""
All four pipettes are loaded into the program, however the app will only
see pipettes that are currently being used.
"""

if pipette_type == 'p300_single':
    pip = instruments.P300_Single(
        mount=mount,
        tip_racks=[tiprack1, tiprack2])
elif pipette_type == 'p10_single':
    pip = instruments.P10_Single(
        mount=mount,
        tip_racks=[tiprack1, tiprack2])
elif pipette_type == 'p50_single':
    pip = instruments.P50_Single(
        mount=mount,
        tip_racks=[tiprack1, tiprack2])
else:
    raise ValueError("Incorrect pipette type.")

plates = [
    plate_1,
    plate_2,
    plate_3,
    plate_4,
    plate_5,
    plate_6]

volumes = [
    VOLUME_ONE,
    VOLUME_TWO,
    VOLUME_THREE,
    VOLUME_FOUR,
    VOLUME_FIVE,
    VOLUME_SIX]

"""
Helper functions
"""


def pre_wet(vol, well):
    pip.aspirate(vol, well)
    pip.dispense(vol, well)


def add_dye(volume, well):
    pip.pick_up_tip(presses=1)
    pre_wet(volume, dye_trough.wells(dye_loc))
    pip.aspirate(volume, dye_trough.wells(dye_loc))
    pip.dispense(volume, well.bottom())
    pip.blow_out()
    pip.return_tip()


"""
Transfer test volumes to each test plate on deck
One plate per test volume, cols 5-12 will be filled by robot
"""

for plate in range(num_plates):
    for col in plates[plate].cols('5', length=8):
        for well in col:
            add_dye(volumes[plate], well)

robot.home()
