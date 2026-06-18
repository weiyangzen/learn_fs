# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser.h

Generic USB-to-serial driver public entry-point header for device-specific serial drivers. It includes `usbser_dsdi.h` and declares soft-state sizing, attach/detach/getinfo/power entry points, and STREAMS open/close/wput/wsrv/rsrv functions.

It also defines default STREAMS packet size and queue watermarks: unlimited max packet size, 128 KiB high water, and 4 KiB low water.
