# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_keyspan/keyspan_var.h

Keyspan USB serial implementation state. It defines supported product IDs, max port count, pre-attach state, firmware record format, PM state, device endpoint specification, control/status message unions for USA19HS and USA49 variants, device state, and per-port state.

`keyspan_state` owns device/port data, a pipe-open semaphore, USBA event/registration handles, default/status/control pipes, logging, USB state, PM state, and USA49WG shared bulk-in pipe tracking. `keyspan_port` owns callbacks, RX/TX queues, TX CV, current control/status messages, baud/LCR/status flags, data pipes, and transfer sizing.

Constants cover port status flags, port states, TX-stopped flag, transfer timeouts and max lengths per model, firmware flag, vendor control requests, debug masks, and common helper prototypes.

Concurrency notes define lock ordering from device state to port to pipe.
