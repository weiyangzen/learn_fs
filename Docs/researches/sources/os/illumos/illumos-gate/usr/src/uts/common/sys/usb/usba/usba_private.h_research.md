# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usba/usba_private.h

## Role

Defines private USBA functions and structures shared inside the USB framework but not intended for client drivers.

## Key Interfaces

- Defines legacy DDK version support constants `USBA_LEG_MAJOR_VER` and `USBA_LEG_MINOR_VER`.
- Declares descriptor parsing helpers for device, configuration, interface association, interface, endpoint, class/vendor descriptors, arbitrary little-endian descriptor data, raw configuration data, and device descriptor retrieval.
- Defines private list type `usba_list_entry_t` plus list initialization, destruction, add/remove, move, leak-check, count, and pop helpers.
- Defines private USBA event tags and suspend/resume event strings.
- Declares DMA attribute lookup, driver binding, ownership, device/interface/interface-association node readiness, bus control, parent notification, usba_device get/set, event data lookup, pipe policy lookup, interrupt-context callback flag adjustment, and interface-number lookup.
- Defines packed standard descriptor sizes and legacy USB 1.1 power descriptor type values.
- Defines configuration and interface power descriptor structures plus parsers.
- Declares ASCII string descriptor conversion.
- Defines `usb_common_power_t` and common PM/event registration helpers for simple USB nexus drivers.

## Risk Notes

These APIs are inside-framework contracts. Descriptor parsers must tolerate extended descriptors while preserving truncation behavior; list and devinfo helpers are used during attach/detach/enumeration and must observe locking expectations.
