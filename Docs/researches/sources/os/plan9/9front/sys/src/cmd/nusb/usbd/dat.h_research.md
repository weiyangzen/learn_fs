# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/usbd/dat.h

## Role

Defines private data structures and constants for `nusb/usbd` hub management.

## Main Contents

The file declares hub descriptor constants for USB2 and USB3 hubs, hub/port feature selector values, port status bits, port state values, timing constants, attach-loop throttling constants, and embedded-driver match flags.

`Hub` stores hub configuration and runtime state: power mode, compound flag, power delay, max current, TT settings, LED support, packet size, port count, port array, failure state, backing `Dev`, and linked-list pointer.

`Port` tracks each hub port: state, last status, attach timing/counter, removable/power-control flags, attached device, and child hub pointer.

`DHub` and `DSSHub` model USB2 and superspeed hub descriptors, including variable-length removable-port bitmaps.
