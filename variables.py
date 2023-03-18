# logfile
logfile = "/var/log/excesspv-to-singleload.service.log" # /var can only be used if run as sudo
# location = "Hinterkirch 3"
location = "G 16"
measurement = "acthor9s"

# initialize general variables
t_cycle = 10 # seconds to pause after one control loop
p_max = 6000 # (Watt) maximum power consumption - at dc_max
p_buffer = 100.0 # (watt) Buffer to not pull from the grid.
p_damp = 0.5 # Dampening factor to avoid oscillation
t_max = 65.0 # °C max temp -> not needed with acthor
t_hyst = 5.0 # °C hysteresis -> not needed with acthor

# initliaze temperature variables -> not needed with acthor
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
max_age = 180 # maximum allowed age in seconds of measurements of p_c before shut down
### G16 STP 10
if_p_consume = "/run/shm/em-3006126044-pconsume" # ID of G16 SMA SHM 2.0 / file name of current consumption over all phases
if_p_supply = "/run/shm/em-3006126044-psupply" # ID of G16 SMA SHM 2.0 / file name of current consumption over all phases
### H3 S10 E3DC
# if_p_consume = "/run/e3dc/ruth-pconsume" # file name of current consumption over all phases
# if_p_supply = "/run/e3dc/ruth-psupply" # file should always contain 0
