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

# initialize pwm
gpio_pin = 24
frequency = 110 # frequency of PWM in Hz
