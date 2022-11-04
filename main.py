# import settings
from variables import *
import influxdbconnector as idb

import time
import RPi.GPIO as GPIO
import os
import glob

import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
    handlers=[
        logging.FileHandler(logfile),
        logging.StreamHandler()
    ],
    datefmt='%Y-%m-%d %H:%M:%S'
)
 
# initialize 1wire for temperature sensors
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# initialize GPIO for PWM
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)
GPIO.setup(gpio_pin_led, GPIO.OUT)
p = GPIO.PWM(gpio_pin, frequency) 
p_led = GPIO.PWM(gpio_pin_led, frequency_led) 
p.start(0)
p_led.start(0)

### temperature functions
t_hyst_bool = False # becomes true if t_max is exceeded to apply hysteresis.

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
    # write to influx db
    try:
        idb.write_point(measurement, ('location', location), ('temperature', temp))
    except:
        logging.error("Writing temperature to influxdb failed.")
    return temp

### power functions
p_c = None
p_h = None
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
    # write to influx db
    try:
        idb.write_point(measurement, ('location', location), ('power_house', p))
    except:
        logging.error("Writing power_house to influxdb failed.")
    return p

def calculate_new_p_c(p_old: float):
    """
    Calculates new power based on old power p_c and p_h to be set on boiler.
    Returns calculated power value or None if error.
    """
    t_c = measure_t_c()
    p_h = measure_p_h()

    # variable for hysteresis
    global t_hyst_bool
    t_max_temp = t_max
    if  t_hyst_bool:
        t_max_temp = t_max - t_hyst

    # calculation of new p_c
    try: 
        if t_c <= t_max_temp: # prüfe ob zu heiß
            if p_h < (-p_damp*p_buffer): # überschuss ja/nein?
                p_c = p_old - p_damp * p_h
            elif p_h > 0: # hysteresis zwischen 0 und p_buffer
                p_c = p_old - p_h - p_buffer
            elif:
		p_c = p_old

            if p_c < 0: # nur Werte > 0 sind sinnvoll
                p_c = 0.0
        else:
            p_c = 0.0
            logging.info(f"The measured temperature is {t_c} °C and exceeds {t_max_temp}. Stop heating.")
    except:
        p_c = 0.0
        logging.exception("")
        logging.error("Error during the calculation of new p_c. Stop heating.")
    
    # activate / deactivate hysteresis for next cycle
    if t_c > t_max:
        t_hyst_bool = True
        logging.info(f"Temperature hysteresis activated.")
    if t_c <= t_max - t_hyst:
        t_hyst_bool = False
        logging.info(f"Temperature hysteresis deactivated.")
    return p_c

def set_new_p_c(p_new: float):
    """
    Writes new p_c to consumption unit.
    Returns set p_c or None if error. 
    """
    # boundaries
    if p_new > 0: # only positive powers
        # calculate new duty cycle load
        if p_new > p_max: # max power is limit
            p_new = p_max
        dc = p_new / p_max * dc_max # linear function mx + b
        logging.info(f"Duty cycle {dc:{1}.{3}} %")
        p.ChangeDutyCycle(dc) 
        # calculate new duty cycle led
        dc_led = dc * dc_max_led/dc_max
        p_led.ChangeDutyCycle(dc_led)
        logging.info(f"Duty cycle of led {dc_led:{1}.{3}} %")
    else:
        p.ChangeDutyCycle(0) # turn load off
        p_led.ChangeDutyCycle(0) # turn led off
    return p_new

def main():
    global p_c
    try:
        while True:
            logging.info('Start of new cycle.')

            p_c = calculate_new_p_c(p_c)
            logging.info(f"New power to be set {p_c} Watts")
            try:
                idb.write_point(measurement, ('location', location), ('target_power', int(p_c)))
            except:
                logging.error("Writing target power to influxdb failed.")

            p_c = set_new_p_c(p_c)
            logging.info(f"New power set to {p_c} Watts")
            try:
                idb.write_point(measurement, ('location', location), ('set_power', int(p_c)))
            except:
                logging.error("Writing set power to influxdb failed.")

            time.sleep(t_cycle)

    except KeyboardInterrupt:
        pass
        # free GPIO settings
        p.stop()
        p_led.stop()
        GPIO.cleanup([gpio_pin, gpio_pin_led])
    except:
        # free GPIO settings
        p.stop()
        p_led.stop()
        GPIO.cleanup([gpio_pin, gpio_pin_led])
        logging.exception("")

logging.info(__name__)
if __name__ == "__main__":
    main()
