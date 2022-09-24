import time
import RPi.GPIO as GPIO
import os
import glob

import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# import settings
from variables import *
 
# initialize 1wire for temperature sensors
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# initialize GPIO for PWM
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)
p = GPIO.PWM(gpio_pin, frequency) 
p.start(0)

### temperature functions
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
        logging.error("Temperature measurement failed.")
    logging.info(f"Measured Temperature is {temp} °C")
    return temp

### power functions
def read_power_file(filename: str, max_age: int):
    """Reads float value from file that contains a single float value.
    The last update of the file is not supposed to be older that "sec" seconds.
    If the file is older or an error occurs the function returns None. 
    Otherwise the value in the file is returned.
    """
    try: 
        with open(filename, 'r') as f:
            output = float(f.read())
        
        age_abs=os.stat(filename)
        age = (time.time()-age_abs.st_mtime) 
        logging.info(f"Age of file {filename} is {age} seconds.")
        if age > max_age:
            output = None
    except:
        output = None
        logging.error(f"Reading of file {filename} failed.")
    return output

def measure_p_h():
    """Measures power at the house-grid connection. 
    Returns power or None if error."""
    p_consume = read_power_file(if_p_consume, max_age)
    p_supply = read_power_file(if_p_supply, max_age)
    try: 
        p = p_consume - p_supply
    except:
        p = None
        logging.error(f"Measurement of power at house-grid connection (p_h) failed.")
    logging.info(f"The current p_h is {p} Watts.")
    return p

def calculate_new_p_c(p_old: float):
    """
    Calculates new power based on old power p_c and p_h to be set on boiler.
    Returns calculated power value or None if error.
    """
    t_c = measure_t_c()
    p_h = measure_p_h()
    try: 
        if t_c <= t_max:
            p_c = p_old - p_h - p_buffer
            if p_c < 0:
                p_c = 0.0
        else:
            p_c = 0.0
            logging.info(f"The measured temperature is {t_c} °C and exceeds {t_max}. Stop heating.")
    except:
        p_c = 0
        logging.error("Error during the calculation of new p_c. Stop heating.")
    return p_c

def set_new_p_c(p_new: float):
    """
    Writes new p_c to consumption unit.
    Returns set p_c or None if error. 
    """
    # boundaries
    if p_new > 0: # only positive powers
        if p_new > p_max: # max power is limit
            p_new = p_max
        dc = p_new / p_max * dc_max # linear function mx + b
        logging.info(f"Duty cycle {dc:{1}.{3}} %")
        p.ChangeDutyCycle(dc) 
    else:
        p.ChangeDutyCycle(0) # turn led off
    return p_new

def main():
    global p_c
    try:
        while True:
            logging.info('Start of new cycle.')
            p_c = calculate_new_p_c(p_c)
            logging.info(f"New power to be set {p_c} Watts")
            p_c = set_new_p_c(p_c)
            logging.info(f"New power to set {p_c} Watts")
            time.sleep(10)
    except KeyboardInterrupt:
        pass
        # free GPIO settings
        p.stop()
        GPIO.cleanup(gpio_pin)

logging.info(__name__)
if __name__ == "__main__":
    main()
