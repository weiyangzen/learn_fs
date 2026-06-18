# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/cdc.c

Read fully: 60 lines, 1105 bytes. SHA-256 prefix: `391a15737254ae37`.

This file provides generic CDC Ethernet reset support. It assumes communication-class devices not claimed by specific controller drivers are standard Ethernet communication devices and tries to load their MAC address from CDC functional descriptors.

`getmac()` scans device descriptors for an Ethernet networking functional descriptor on a communication/ethernet interface, loads the string descriptor containing the 12-hex-digit MAC address, validates length, and parses it into `ether->addr`.

`cdcreset()` applies this generic path only when the USB device class is communications; specific controller probes are expected to run first.

Integration: part of the shared USB Ethernet driver stack and depends on helper functions from `ether.h` such as `parseaddr()`.

Risk notes: it ignores CDC union descriptors and only retrieves the MAC address; endpoint/interface pairing is left to the generic Ethernet framework. Devices with nonstandard descriptors may need a specific driver.
