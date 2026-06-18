# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsprl/pl2303_var.h

Internal Prolific PL2303 USB serial state. It defines PM state, chip type enum, per-device `pl2303_state_t`, port/pipe states, tunables, debug masks, and `NELEM`.

`pl2303_state_t` tracks lock, devinfo, device flags, port state/flags, generic serial callbacks, USBA event/registration/default/bulk pipe handles and states, log handle, USB device state, transfer size, PM state, RX/TX mblks, TX completion CV, modem controls, and detected chip type.

Chip types distinguish PL-2303H, PL-2303X/HX chip A, PL-2303HX chip D, and unknown.
