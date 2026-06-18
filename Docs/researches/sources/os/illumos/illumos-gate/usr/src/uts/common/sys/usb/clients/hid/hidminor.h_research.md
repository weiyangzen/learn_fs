# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/hid/hidminor.h

## Purpose
USB HID minor number encoding helpers.

## Main Interfaces
- Defines masks and shifts for HID minor bits, ugen bits, and instance bits.
- Defines internal minor marker `HID_MINOR_INTERNAL`.
- Defines macros to mark/test internal opens, test ugen opens, extract instance numbers, and construct internal or external minors.

## Dependencies And Relationships
Used by the USB HID driver when creating and decoding device minor numbers for internal HID consumers and external generic USB access.

## Research Notes
The minor encoding reserves bit space for internal opens and ugen-style external opens, so all consumers should use these macros instead of hand-decoding minors.
