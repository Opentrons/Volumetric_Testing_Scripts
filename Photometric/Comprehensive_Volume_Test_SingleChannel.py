"""
@author opentrons
@date December 20th, 2017
@version V1.1
"""
from opentrons import containers, instruments, robot

# Change the volumes you are testing here
VOLUME_ONE = 10
VOLUME_TWO = 9
VOLUME_THREE = 8
VOLUME_FOUR = 7
VOLUME_FIVE = 6

# Choose the amount of plates you would like to run
num_plates = 1
pipette_type = 'p10_single'
# labware definitions
tiprack1 = containers.load('tiprack-200ul', '3', 'Tiprack 1')
tiprack2 = containers.load('tiprack-200ul', '6', 'Tiprack 2')
dye_trough = containers.load('trough-12row', '9', 'Dye Trough')

"""
Below are 8 separate 96 well plates that can be processed.
They are separated out into half full plates and full plates.
If you wish to run all of the plates as one setting see below.
The numbers next to the plate represents the slot number
"""
plate_1 = containers.load('96-flat', '1')
plate_2 = containers.load('96-flat', '2')
plate_3 = containers.load('96-flat', '4')
plate_4 = containers.load('96-flat', '5')

plate_5 = containers.load('96-flat', '7')
plate_6 = containers.load('96-flat', '8')
plate_7 = containers.load('96-flat', '10')
plate_8 = containers.load('96-flat', '11')

"""
All four pipettes are loaded into the program, however the app will only
see pipettes that are currently being used.
"""

if pipette_type == 'p300_single':

    pip = instruments.P300_Single(
        tip_racks=[tiprack1, tiprack2],
        mount='right')
elif pipette_type == 'p10_single':
    pip = instruments.P10_Single(
        mount='right',
        tip_racks=[tiprack1, tiprack2])

    pip.ul_per_mm = 0.678
else:
	raise ValueError("Incorrect pipette type.")


plates = [
    plate_1,
    plate_2,
    plate_3,
    plate_4,
    plate_5,
    plate_6,
    plate_7,
    plate_8]


"""
Helper functions
"""


def pre_wet(well):
    pip.aspirate(10, well)
    pip.dispense(10, well)


def add_dye(volume, well):
    pip.pick_up_tip(presses=1)
    pre_wet(dye_trough[0])
    pip.aspirate(volume, dye_trough[0])
    pip.dispense(volume, well.bottom())
    pip.blow_out()
    pip.return_tip()


"""
Creates a list of plate configurations
so that you don't have to keep writing the
same code over again.
"""
# wells to add dye to
dye_test_one = []
dye_test_two = []
dye_test_three = []
dye_test_four = []
dye_test_five = []

# Plate 1 configuration

dye_test_one.append([plate_1.rows('3', length=2)])
dye_test_two.append([plate_1.rows('5', length=2)])
dye_test_three.append([plate_1.rows('7', length=2)])
dye_test_four.append([plate_1.rows('9', length=2)])
dye_test_five.append(plate_1.rows('11', length=2))

# Plate 2 configuration (if you want not put a die in the plate, simply
# add an empty list)



for val in range(num_plates):
    if val == 1:
        VOLUME_ONE = 5
        VOLUME_TWO = 4
        VOLUME_THREE = 3
        VOLUME_FOUR = 2
        VOLUME_FIVE = 1

    for row in dye_test_one[val]:
        for well in row:
            add_dye(VOLUME_ONE, well)

    for row in dye_test_two[val]:
        for well in row:
            add_dye(VOLUME_TWO, well)
 
    for row in dye_test_three[val]:
        for well in row:
            add_dye(VOLUME_THREE, well)

    for row in dye_test_four[val]:
        for well in row:
            add_dye(VOLUME_FOUR, well)

    for row in dye_test_five[val]:
        for well in row:
            add_dye(VOLUME_FIVE, well)

robot.home()

