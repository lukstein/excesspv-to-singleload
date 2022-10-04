# initialize general variables
t_cycle = 10 # seconds to pause after one control loop
p_h = 0.0 # (Watt) current power at house-grid-connection
p_c = 0.0 # (Watt) current power to zero
p_max = 2000 # (Watt) maximum power consumption - at dc_max
p_buffer = 100.0 # (watt) Buffer to not pull from the grid.
t_c = 25.0 # °C current temperature
t_max = 75.0 # °C max temp

# initliaze temperature variables
t_sensorname = "28-0000000d756b" # ID of 1-Wire temperature sensor
base_dir = '/sys/bus/w1/devices/' # not to change
device_file = base_dir + t_sensorname + '/w1_slave' # not to change

# initialize pwm
gpio_pin = 24
frequency = 150 # frequency of PWM in Hz
dc_max = 100 # for leds max duty cycle power restriction
gpio_pin_led = 23
frequency_led = 150 # frequency of PWM in Hz
dc_max_led = 30 # for leds max duty cycle power restriction


# initialize power variables
if_p_consume = "/run/shm/em-3006126044-pconsume" # ID of G16 SMA SHM 2.0 / file name of current consumption over all phases
if_p_supply = "/run/shm/em-3006126044-psupply" # ID of G16 SMA SHM 2.0 / file name of current consumption over all phases
max_age = 180 # maximum allowed age in seconds of measurements of p_c before shut down