Install the modified python-ant available on our github : https://github.com/cowboy-coders/python-ant

start pyro4 naming server : python -m Pyro4.naming

start pyro4 antnode servers : python ant-server.py (if you have two usb sticks you can start ant-server2.py aswell - used with the man in the middle attack as was getting collisons with the one stick using two channels )

either use : python bushido_middle.py to setup as man in the middle (you can change injections.py when running to change values or bytes in data packet)
or : python bushido_logger.py for a 'pc connection' to headunit 

please note: can either monitor ant traffic with wireshark plugin (on github) or log data packets directly via python

known bugs: server has stability issues and occasionally crashes requiring a replug of the antstick and restart of antnode server (possibly a bug I introduced when adding support for extended messages in ant-python)
