# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/usb.h

Primary USB userspace library header.

Defines:
- USB constants: endpoint/config/interface limits, request type bits, standard requests, class IDs, descriptor types/sizes, feature selectors, device states, endpoint directions/types, config attributes, and HID report item constants.
- Core structs: `Dev`, `Usbdev`, `Ep`, `Altc`, `Iface`, `Conf`, raw descriptor wrappers, and standard descriptor layouts.
- CSP helper macros, little-endian GET/PUT macros, debug macros, and `%U` formatter declaration.
- USB library API for device opening, descriptor loading/parsing, control requests, endpoint opening, device discovery, driver startup, and utility allocation.

This is the shared ABI for all Plan 9 USB command drivers in this group.
