# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbftdi/uftdi_var.h

Internal FTDI device-specific serial driver state. It includes USB serial DSDI support and defines PM state, soft register cache, and per-device `uftdi_state_t`.

`uftdi_state_t` tracks DDI/USBA handles, device and port flags/states, hardware port number, callbacks into the generic serial driver, default/bulk pipe handles and states, buffer sizes, PM state, RX/TX mblk ownership, TX completion CV, cached baud/data/flow registers, modem control, modem status, and line status.

Constants define port states, TX-stopped flag, pipe states, bulk timeouts, max transfer size, cleanup level, and debug masks.
