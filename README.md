# excesspv-to-singleload
This script detects excess PV power and supplies this power to an ohm type load. It runs on a RPi 3B+. The load is controlled via PWM through a Kemo M240. 

## Service
The application works as a service. To make the script a service copy the file excesspv-to-singleload.service to /etc/systemd/system/ and reload the deamons, enable and start.

Code to execute:
```sudo systemctl daemon-reload
sudo systemctl enable flashled.service
sudo systemctl start flashled.service```

