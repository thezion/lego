# pylint: disable=assignment-from-no-return

"""
Download to the Move Hub and run the app:
======================================================
pybricksdev run ble --name "PB Move Hub" move_hub_1.py
======================================================
"""

from pybricks.hubs import MoveHub
from pybricks.pupdevices import Motor, ColorDistanceSensor
from pybricks.parameters import Button, Color, Port
from pybricks.tools import wait
from pybricks.pupdevices import Remote

# ====== ====== ====== ====== ====== ====== ====== ======

hub = MoveHub()
hub_battery = hub.battery.current()

motor_a = Motor(Port.A)
motor_b = Motor(Port.B)

distance = ColorDistanceSensor(Port.D)

remote: Remote = None
remote_tries: int = 5
remote_connected: bool = False

# ====== ====== ====== ====== ====== ====== ====== ======


def update_speed(original_power: int) -> int:
    """
    Update motor power and blink the light

    Args:
        original_power (int): The original power of the motor.

    Returns:
        int: The new power of the motor.
    """
    new_power = original_power + 20
    if new_power > 100:
        new_power = 40
    print(f"Motor power = {new_power}")
    blinks = new_power // 20
    while blinks > 0:
        wait(100)
        remote.light.on(Color.VIOLET)
        wait(100)
        remote.light.off()
        blinks -= 1
    remote.light.on(Color.GREEN)
    return new_power


def main():
    """
    What to do after the devices are ready.
    """
    power: int = 60  # initial wheel power
    turn_power: int = 80  # fixed turn power
    loops: int = 0
    estimated_distance: int = 100
    danger_distance: int = 50

    while True:
        pressed = remote.buttons.pressed()
        hub_press = hub.buttons.pressed()

        # ====== distance ======

        if loops % 5 == 0:
            estimated_distance = distance.distance()
            # print(f"Estimated distance: {estimated_distance}")

        # ====== move ======

        if Button.RIGHT_PLUS in pressed:
            # turn right
            motor_a.dc(-turn_power)
            motor_b.dc(-turn_power)
        elif Button.RIGHT_MINUS in pressed:
            # turn left
            motor_a.dc(turn_power)
            motor_b.dc(turn_power)
        else:
            # go forward
            if Button.LEFT_PLUS in pressed:
                if estimated_distance > danger_distance:
                    motor_a.dc(power-5)  # somehow motor a is stronger
                    motor_b.dc(-power)
                else:
                    # hitting a wall?
                    motor_a.stop()
                    motor_b.stop()
                    remote.light.on(Color.RED)
                    wait(100)
                    remote.light.on(Color.GREEN)
            # go backward
            elif Button.LEFT_MINUS in pressed:
                motor_a.dc(-(power-1))
                motor_b.dc(power)
            else:
                motor_a.stop()
                motor_b.stop()

        if Button.LEFT in pressed:
            power = update_speed(power)

        # ====== utils ======

        if Button.CENTER in hub_press:
            print("Bye bye!")
            wait(500)
            hub.system.shutdown()
            break

        # ====== next tick ======
        wait(100)
        loops += 1


# ====== ====== ====== ====== ====== ====== ====== ======


for _ in range(5):
    print()
print("Running app...")
print(f"Current battery: {hub_battery}%")

# blink white light to indicate the app is searching for remote
hub.light.blink(Color.WHITE, [200, 100, 200, 1000])

while remote_tries > 0:
    wait(1000)
    remote_tries -= 1
    print(f"Connecting to remote ... {5-remote_tries} / 5")
    try:
        remote = Remote()
        remote_connected = True
        break
    except Exception as e:
        print(f"Timeout connecting to remote! {e}")

if remote_connected:
    print("Remote connected!")
    hub.light.on(Color.YELLOW if hub_battery < 20 else Color.GREEN)
    remote.light.on(Color.GREEN)
    main()  # run major logic
else:
    hub.light.on(Color.RED)
    wait(3000)
    print("Remote not connected - exit app")
