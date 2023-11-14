# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import gc
import os
from flashbdev import bdev
import time
import machine, sdcard
from ledColor import ledColor
from machine import Pin, SPI

version = 2.20

p3 = Pin(3,Pin.OUT)
p3.value(1)
time.sleep(0.25)
spi = SPI(1, baudrate=10000000, polarity=0, phase=0, sck=Pin(4), mosi=Pin(6), miso=Pin(5))
sd = None

def check_bootsec():
    buf = bytearray(bdev.ioctl(5, 0))  # 5 is SEC_SIZE
    bdev.readblocks(0, buf)
    empty = True
    for b in buf:
        if b != 0xFF:
            empty = False
            break
    if empty:
        return True
    fs_corrupted()


def fs_corrupted():
    import time
    import micropython

    # Allow this loop to be stopped via Ctrl-C.
    micropython.kbd_intr(3)

    while 1:
        print(
            """\
The filesystem appears to be corrupted. If you had important data there, you
may want to make a flash snapshot to try to recover it. Otherwise, perform
factory reprogramming of MicroPython firmware (completely erase flash, followed
by firmware programming).
"""
        )
        time.sleep(3)

def mount_internal():
    try:
        os.stat('boot.py')
    except OSError:
        print('Writing boot file')
        with open("boot.py", "w") as f:
            f.write(
            '''\
# This file is executed on every boot (including wake-boot from deepsleep)
# Delete 'main.py', 'boot.py', 'test.py', or 'network_cfg.py' to automatically replace them with the default version on reboot
# This behavior can be changed by replacing this file with your own

#import esp
#esp.osdebug(None)
from ledColor import ledColor

ledColor(0,0,0) # turn led off

try:
    os.stat('network_cfg.py')
except OSError:
    print('Writing network config file')
    with open("network_cfg.py", "w") as s:
        s.write(
            """\
STA_SSID = 'your_WiFi_SSID_here'
STA_PASS = 'your_WiFi_PASS_here'
"""
        )

try:
    os.stat('test.py')
except OSError:
    print('Writing test file')
    with open("test.py", "w") as t:
        t.write(
            """\
import sys

print('This is a test file. You can modify it in any way. To replace it with the default version, simply delete it from the sd card. It will be replaced automatically.')

del sys.modules['test'] # this allows you to keep importing test
"""
        )
        
try:
    os.stat('main.py')
except OSError:
    print('Writing main file')
    with open("main.py", "w") as m:
        m.write(
            """\
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import webrepl
import network
import machine
from ledColor import ledColor
import time 
import os


if 'webrepl_cfg.py' in os.listdir():
    if 'network_cfg.py' in os.listdir():
        from network_cfg import STA_SSID, STA_PASS
        if(STA_SSID == 'your_WiFi_SSID_here'): # if STA credentials haven't been set
            print('Edit network_cfg.py with your credentials to enable WebREPL')
        else:
            print('Attempting to connect to', STA_SSID)
            # Set up WebREPL over STA
            sta_if = network.WLAN(network.STA_IF) # configure STA
            sta_if.active(True)                # turn on STA
            sta_if.connect(STA_SSID, STA_PASS) # Connect to an STA network
    
            for i in range(10):
                if sta_if.isconnected() == False:
                    ledColor(32,16,0) # turn led yellow to show we're trying to connect to sta_if
                    time.sleep(0.25) # wait 250ms
                    ledColor(0,0,0) # turn led off
                    time.sleep(0.75)
            
            if sta_if.isconnected():
                print('Connected to', STA_SSID)
                ledColor(0,32,0) # turn led green to show sta_if is connected 
                time.sleep(0.25) # wait 250ms
                ledColor(0,0,0) # turn led off
                webrepl.start() # Start WebREPL
            else:
                print('Connection to', STA_SSID, 'failed')
                sta_if.disconnect()
                sta_if.active(False) # disable sta_if connection
                ledColor(32,0,0) # prepare to turn led red to show sta_if isn't connected 
                time.sleep(0.25) # wait 250ms
                ledColor(0,0,0) # prepare ro turn led off
            print('Type', "os.remove('network_cfg.py')", 'to disable WebREPL')
else:
    print('Type "import webrepl_setup" to use WebREPL')
"""
        )
'''
            )

def mount_external():
    try:
        os.stat('/sd/src')
    except OSError:
        os.mkdir('/sd/src')
    
    try:
        os.stat('/sd/src/microPython')
    except OSError:
        os.mkdir('/sd/src/microPython')
    
    try:
        os.stat('/sd/src/microPython/boot.py')
    except OSError:
        print('Writing boot file')
        with open("/sd/src/microPython/boot.py", "w") as f:
            f.write(
            '''\
# This file is executed on every boot (including wake-boot from deepsleep)
# Delete 'main.py', 'boot.py', 'test.py', or 'network_cfg.py' to automatically replace them with the default version on reboot
# This behavior can be changed by replacing this file with your own

#import esp
#esp.osdebug(None)
from ledColor import ledColor

ledColor(0,0,0) # turn led off

try:
    os.stat('/sd/src/microPython/network_cfg.py')
except OSError:
    print('Writing network config file')
    with open("/sd/src/microPython/network_cfg.py", "w") as s:
        s.write(
            """\
STA_SSID = 'your_WiFi_SSID_here'
STA_PASS = 'your_WiFi_PASS_here'
"""
        )

try:
    os.stat('/sd/src/microPython/test.py')
except OSError:
    print('Writing test file')
    with open("/sd/src/microPython/test.py", "w") as t:
        t.write(
            """\
import sys

print('This is a test file. You can modify it in any way. To replace it with the default version, simply delete it from the sd card. It will be replaced automatically.')

del sys.modules['test'] # this allows you to keep importing test
"""
        )
        
try:
    os.stat('/sd/src/microPython/main.py')
except OSError:
    print('Writing main file')
    with open("/sd/src/microPython/main.py", "w") as m:
        m.write(
            """\
# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)

import webrepl
import network
import machine
from ledColor import ledColor
import time 
import os


if 'webrepl_cfg.py' in os.listdir():
    if 'network_cfg.py' in os.listdir():
        from network_cfg import STA_SSID, STA_PASS
        if(STA_SSID == 'your_WiFi_SSID_here'): # if STA credentials haven't been set
            print('Edit network_cfg.py with your credentials to enable WebREPL')
        else:
            print('Attempting to connect to', STA_SSID)
            # Set up WebREPL over STA
            sta_if = network.WLAN(network.STA_IF) # configure STA
            sta_if.active(True)                # turn on STA
            sta_if.connect(STA_SSID, STA_PASS) # Connect to an STA network
    
            for i in range(10):
                if sta_if.isconnected() == False:
                    ledColor(32,16,0) # turn led yellow to show we're trying to connect to sta_if
                    time.sleep(0.25) # wait 250ms
                    ledColor(0,0,0) # turn led off
                    time.sleep(0.75)
            
            if sta_if.isconnected():
                print('Connected to', STA_SSID)
                ledColor(0,32,0) # turn led green to show sta_if is connected 
                time.sleep(0.25) # wait 250ms
                ledColor(0,0,0) # turn led off
                webrepl.start() # Start WebREPL
            else:
                print('Connection to', STA_SSID, 'failed')
                sta_if.disconnect()
                sta_if.active(False) # disable sta_if connection
                ledColor(32,0,0) # prepare to turn led red to show sta_if isn't connected 
                time.sleep(0.25) # wait 250ms
                ledColor(0,0,0) # prepare ro turn led off
            print('Type', "os.remove('network_cfg.py')", 'to disable WebREPL')
else:
    print('Type "import webrepl_setup" to use WebREPL')
"""
        )
'''
            )
    os.chdir('/sd/src/microPython')

try:
    if bdev:
        os.mount(bdev, "/")
except OSError:
    ledColor(255,0,0) # turn led red
    check_bootsec()
    print("Performing initial setup")
    if bdev.info()[4] == "vfs":
        os.VfsLfs2.mkfs(bdev)
        vfs = os.VfsLfs2(bdev)
    elif bdev.info()[4] == "ffat":
        os.VfsFat.mkfs(bdev)
        vfs = os.VfsFat(bdev)
    os.mount(vfs, "/")
    print('Setup Complete')

ledColor(0,0,0) # turn led off

# Check If SD Card is present
useInternal = False;
imReason = ''
try:
    sd = sdcard.SDCard(spi, Pin(1))
except:
    useInternal = True
    imReason = 'No SD Card Detected'

# If SD Card is Present, Attempt to Mount it
if(useInternal == False):
    try:
        os.mount(sd, '/sd')
    except:
        # retry
        time.sleep(0.25)
        try:
            os.mount(sd, '/sd')
        except:
            useInternal = True
            imReason = 'Failed to Mount SD Card'
        
        
        
if(useInternal == True):
    mount_internal()
    time.sleep(0.5)
    print() # print empty line so future messages are separate from boot message
    print('microPython for DDC3: "Innovation of Creation"')
    print('Firmware Version:', version, '[ by Defiance Digital ]')
    print(imReason)
    print('File System Located in Flash')
else:
    mount_external()
    time.sleep(0.5)
    print() # print empty line so future messages are separate from boot message
    print('microPython for DDC3: "Innovation of Creation"')
    print('Firmware Version:', version, '[ by Defiance Digital ]')
    print('File System Located at /src/microPython on sd card')
    
gc.collect()
