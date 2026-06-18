# File Research: sources/os/bsd/netbsd-src/lib/libusbhid/usbvar.h

## Purpose
Defines the private `struct report_desc` used by `libusbhid` to carry a USB HID report descriptor.

## Key Details
- Contains only a variable-length descriptor container:
  - `unsigned int size`
  - `unsigned char data[1]`
- The one-byte trailing array is the historical C idiom for variable-sized allocation.

## Dependencies and Role
- No includes or function declarations.
- Used as a compact ABI/data structure boundary for HID descriptor parsing code.
