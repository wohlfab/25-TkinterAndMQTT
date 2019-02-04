"""
Using a Brickman (robot) as the receiver of messages.
"""
import mqtt_remote_method_calls as com
import time
import math
import ev3dev.ev3 as ev3

class DelegateThatReceives(object):
    def __init__(self):
        self.robot = DriveSystem()

    def move(self, stat1, stat2):
        self.robot.go(stat1, stat2)
        print(stat1, stat2)

    def end(self, message):
        self.robot.stop()
        print("STOP!")


def main():
    name1 = input("Enter one name (subscriber): ")
    name2 = input("Enter another name (publisher): ")
    robot = DelegateThatReceives()
    mqtt_client = com.MqttClient(robot)
    mqtt_client.connect(name1, name2)
    time.sleep(1)  # Time to allow the MQTT setup.
    print()

    while True:
        time.sleep(0.01)  # Time to allow message processing


class DriveSystem(object):
    """
    Controls the robot's motion via GO and STOP methods,
        along with various methods that GO/STOP under control of a sensor.
    """

    def __init__(self):
        """
        What comes in:  Two (optional) sensors.
        What goes out:  Nothing, i.e., None.
        Side effects:
          -- Stores the (optional) sensors.
          -- Constructs two Motors (for the left and right wheels).
        Type hints:
          :type color_sensor:              ColorSensor
          :type infrared_proximity_sensor: InfraredProximitySensor
        """
        self.left_motor = Motor('B')
        self.right_motor = Motor('C')


    def go(self, left_wheel_speed, right_wheel_speed):
        self.left_motor.turn_on(left_wheel_speed)
        self.right_motor.turn_on(right_wheel_speed)

    def stop(self):
        self.left_motor.turn_off()
        self.right_motor.turn_off()

    def go_straight_for_seconds(self, seconds, speed):
        start = time.time()
        self.go(speed, speed)
        # Note: using   time.sleep   to control the time to run is better.
        # We do it with a WHILE loop here for pedagogical reasons.
        while True:
            if time.time() - start >= seconds:
                self.stop()
                break

    def go_straight_for_inches_using_time(self, inches, speed):
        # NOTE to students:  The constant and formula below are not accurate
        seconds_per_inch_at_100 = 10.0  # 1 sec = 10 inches at 100 speed
        seconds = abs(inches * seconds_per_inch_at_100 / speed)

        self.go_straight_for_seconds(seconds, speed)

    def go_straight_for_inches_using_sensor(self, inches, speed):
        self.left_motor.reset_position()
        inches_per_degree = self.left_motor.WheelCircumference/360
        desire = inches/inches_per_degree
        self.go(speed, speed)
        val = 0
        while True:
            current = abs(self.left_motor.get_position())
            val = val + current
            if val >= desire:
                break
            self.left_motor.reset_position()
        self.stop()



    def go_straight_until_black(self, speed):
        """
        Goes straight at the given speed until the robot is over
        a black surface, as measured by the color sensor.
        """
        self.go(speed, speed)
        while True:
            color = ColorSensor(3)
            if color.get_reflected_light_intensity() <= 10:
                break
        self.stop()

    def go_forward_until_distance_is_less_than(self, inches, speed):
        """
        Goes forward at the given speed until the distance
        to the nearest object, per the infrared proximity sensor,
        is less than the given number of inches.
        """
        pass

    def tones_until_touch_sensor_is_pressed(self):
        """
        Plays an increasing sequence of short tones,
        stopping when the touch sensor is pressed.
        """
        pass


###############################################################################
# Classes built directly upon the underlying EV3 robot modules:
#   -- Motor
#   -- TouchSensor
#   -- ColorSensor
#   -- IR_DistanceSensor
#   -- Beeper
#   -- ToneMaker
# USE them, but do NOT modify them.
###############################################################################
class Motor(object):
    WheelCircumference = 1.3 * math.pi

    def __init__(self, port, motor_type='wheel'):
        # port must be 'A', 'B', 'C', or 'D'.  Use 'arm' as motor_type for Arm.
        if motor_type == 'wheel':
            self._motor = ev3.LargeMotor('out' + port)
        else:
            self._motor = ev3.MediumMotor('out' + port)

    def turn_on(self, speed):  # speed must be -100 to 100
        self._motor.run_direct(duty_cycle_sp=speed)

    def turn_off(self):
        self._motor.stop(stop_action="brake")

    def get_position(self):  # Units are degrees (that the motor has rotated).
        return self._motor.position

    def reset_position(self):
        self._motor.position = 0


class TouchSensor(object):
    def __init__(self, port):  # port must be 1, 2, 3 or 4
        self._touch_sensor = ev3.TouchSensor('in' + str(port))

    def is_pressed(self):
        """ Returns True if this TouchSensor is pressed, else returns False """
        return self._touch_sensor.is_pressed


class ColorSensor(object):
    def __init__(self, port):  # port must be 1, 2, 3 or 4
        self._color_sensor = ev3.ColorSensor('in' + str(port))

    def get_reflected_light_intensity(self):
        """
        Shines red light and returns the intensity of the reflected light.
        The returned value is from 0 to 100,
        but in practice more like 3 to 90+ in our classroom lighting
        with our downward-facing XXX-inches-from-the-ground sensor placement.
        """
        return self._color_sensor.reflected_light_intensity


class InfraredProximitySensor(object):
    def __init__(self, port):
        self._ir_sensor = ev3.InfraredSensor('in' + str(port))

    def get_distance(self):  # port must be 1, 2, 3 or 4
        """
        Returns the distance to the nearest object sensed by this IR sensor.
        Units are: XXX.
        """
        # DCM: Fix above units XXX and add info re width of range.
        return self._ir_sensor.proximity


class Beeper(object):
    def __init__(self):
        self._beeper = ev3.Sound

    def beep(self):
        # DCM: Indicate that this is NON-blocking.
        # DCM: Indicate that returns a subprocess.Popen, which has a WAIT method
        return self._beeper.beep()


class ToneMaker(object):
    def __init__(self):
        self._tone_maker = ev3.Sound

    def tone(self, frequency, duration):
        # DCM: Indicate that this is NON-blocking.
        # DCM: Indicate that returns a subprocess.Popen, which has a WAIT method
        return self._tone_maker.tone(frequency, duration)  # MHz, msec  DCM XXX CTO


# -----------------------------------------------------------------------------
# Calls  main  to start the ball rolling.
# -----------------------------------------------------------------------------
main()

main()
# Same as m2_fake_robot_as_mqtt_sender,
# but have the robot really do the action.
# Implement just FORWARD at speeds X and Y is enough.
