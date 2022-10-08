# excesspv-to-singleload
This script detects excess PV power and supplies this power to an ohm type load. It runs on a RPi 3B+. The load is controlled via PWM through a Kemo M240. The measurement of the power it self needs to be supplied by an additional service. See links in the supported power measurements.

## Supported Power Measurements
* SMA SHM 2.0 via Multicast - check out this https://www.unifox.at/software/sma-em-daemon/

## Service in Linux
The application works as a service. To make the script a service copy the file excesspv-to-singleload.service to /etc/systemd/system/ and reload the deamons, enable and start.

Code to execute to start service:
```
sudo systemctl daemon-reload
sudo systemctl enable flashled.service
sudo systemctl start flashled.service
```
## Configuration
Variables are defined in `variables.py`.

## Log and log streaming
The script writes logs to the logfile defined `variables.py`. The logs can be streamed using the frontail node.js framework. 
Node.js, npm and in the following frontail need to be installed:
```
sudo apt install nodejs npm
sudo npm i frontail -g
```
Once installed, the service frontail.service can be installed equivalently like the excesspv service but using the file `frontail.service`.

Link to frontail: https://github.com/mthenw/frontail


## Pin setup on RPi
<img src="https://github.com/lukstein/excesspv-to-singleload/blob/main/singleload%20pinbelegung.png" alt="RPi 3B+ Pin usage" title="Pin usage" width="400"/>

## Program flow
<img src="https://github.com/lukstein/excesspv-to-singleload/blob/main/programmablauf%20singleload.png" alt="Program flow" title="Program flow" width="300"/>
