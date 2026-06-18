# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbsacm/usbsacm.h

USB CDC ACM serial driver private state. It defines PM state, per-port `usbsacm_port`, per-device `usbsacm_state`, pipe/port state enums, timeouts, class request type constants, and debug masks.

Each ACM port owns bulk-in, bulk-out, and interrupt pipes, endpoint descriptor, control/data interface numbers, data-port number, generic serial callbacks, RX/TX messages, TX completion CV, modem controls in/out, capability bits, line coding, port state, and bulk-in transfer size.

The device state owns DDI/USBA handles, USB events, default pipe, logging, device state, transfer size, compatibility flag, port array/count, and PM state.
