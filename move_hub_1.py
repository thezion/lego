"""
Download to the Move Hub and run the app:
======================================================
pybricksdev run ble --name "PB Move Hub" move_hub_1.py
======================================================
"""

from pybricks.hubs import MoveHub
from pybricks.pupdevices import Motor
from pybricks.parameters import Button, Color, Port
from pybricks.tools import wait
from pybricks.pupdevices import Remote

# ====== ====== ====== ====== ======

hub = MoveHub()
hub_battery = hub.battery.current()  # pylint: disable=E1111

motor_a = Motor(Port.A)
motor_b = Motor(Port.B)

remote: Remote = None
remote_tries: int = 5
remote_connected: bool = False

# ====== ====== ====== ====== ======


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
    power: int = 60

    while True:
        pressed = remote.buttons.pressed()  # pylint: disable=E1111
        hub_press = hub.buttons.pressed()  # pylint: disable=E1111

        # ====== remote ======

        if Button.LEFT_PLUS in pressed:
            motor_b.dc(-power)
        elif Button.LEFT_MINUS in pressed:
            motor_b.dc(power)
        else:
            motor_b.stop()

        if Button.RIGHT_PLUS in pressed:
            motor_a.dc(power)
        elif Button.RIGHT_MINUS in pressed:
            motor_a.dc(-power)
        else:
            motor_a.stop()

        if Button.LEFT in pressed:
            power = update_speed(power)

        # ====== remote ======

        if Button.CENTER in hub_press:
            print("Bye bye!")
            hub.system.shutdown()
            break

        # ====== next tick ======
        wait(100)


# ====== ====== ====== ====== ======


for _ in range(5):
    print()
print("Running app...")
print(f"Current battery: {hub_battery}%")

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
        print(f"Fail to connect to remote! {e}")

if remote_connected:
    print("Remote connected!")
    hub.light.on(Color.YELLOW if hub_battery < 20 else Color.GREEN)
    remote.light.on(Color.GREEN)
    main()
else:
    hub.light.on(Color.RED)
    wait(3000)
    print("Remote not connected - exit app")
