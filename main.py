import time
import RPi.GPIO as GPIO
import os
import glob 
 
# initialize 1wire
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# initialize GPIO
GPIO.setmode(GPIO.BCM)
gpio_pin = 24
GPIO.setup(gpio_pin, GPIO.OUT)
p = GPIO.PWM(gpio_pin, 500)  # frequency=500Hz
p.start(0)


# initialize general variables
p_h = 0.0 # (Watt) current power at house-grid-connection
p_c = 0.0 # (Watt) current power to zero
p_max = 2000 # (Watt) maximum power consumption
p_buffer = 100.0 # (watt) Buffer to not pull from the grid.
t_c = 25.0 # °C current temperature
t_max = 75.0 # °C max temp

# initliaze temperature variables
t_sensorname = "28-0000000d756b" # ID of 1-Wire temperature sensor
base_dir = '/sys/bus/w1/devices/' # not to change
device_file = base_dir + t_sensorname + '/w1_slave' # not to change

def read_temp_raw():
    """Reads raw output file of 1 wire protocol of the specified sensor.
    """
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def measure_t_c():
    """Measures current temperature of boiler.
    Returns temperature or None if error."""
    try: 
        temp = read_temp()
    except:
        temp = None
    return temp

def measure_p_h():
    """Measures power at the house-grid connection. 
    Returns power or None if error."""
    temp = input("Enter current P_h (Watts):")
    return float(temp)

def calculate_new_p_c(p_old: float):
    """
    Calculates new power based on old power p_c and p_h to be set on boiler.
    Returns calculated power value or None if error.
    """
    t_c = measure_t_c()
    p_h = measure_p_h()
    if t_c <= t_max:
        p_c = p_old - p_h - p_buffer
        if p_c < 0:
            p_c = 0.0
    else:
        p_c = 0.0
    return p_c

def set_new_p_c(p_new: float):
    """
    Writes new p_c to consumption unit.
    Returns set p_c or None if error. 
    """
    # boundaries
    dc_max = 50 # for leds max duty cycle power restriction

    if p_new > 0: # only positive powers
        if p_new > p_max: # max power is limit
            p_new = p_max
        dc = p_new / p_max * dc_max # linear function mx + b
        print(f"Duty cycle {dc:{1}.{3}} %")
        p.ChangeDutyCycle(dc) # turn led on, 50% is enough for leds
    else:
        p.ChangeDutyCycle(0) # turn led off
    return p_new

try:
    while True:
        p_c = calculate_new_p_c(p_c)
        print(f"New power to be set {p_c} Watts")
        p_c = set_new_p_c(p_c)
        print(f"New power to set {p_c} Watts")
except KeyboardInterrupt:
    pass
    # free GPIO settings
    p.stop()
    GPIO.cleanup(gpio_pin)
