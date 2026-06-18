# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/privsep.h

## Purpose
Defines the dhclient privilege-separation message structures and message codes.

## Main Elements
- `struct buf`: byte buffer with size, write position, and read position.
- `enum imsg_code`: message types for script initialization, parameter writing, script execution and return, packet sending, and interface MTU setting.
- `struct imsg_hdr`: message code and total message length.

## Dependencies And Integration
Included by privilege-separation implementation and callers constructing messages. Message codes drive `dispatch_imsg()` switch behavior.

## Risk Notes
The protocol uses native `size_t` and struct layouts across forked processes on the same host, not a stable cross-platform wire format.
