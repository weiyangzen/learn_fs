# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbser/usbser_var.h

Internal generic USB serial driver state. It defines per-port worker-thread metadata, global device state, per-port tty state, port state machine, activities, flags, minor-number layout, timeouts, debug masks, and macros dispatching to DSD operations.

`usbser_state` tracks device list linkage, devinfo, mutex, soft-state anchor, instance, DSD ops/handle, port count/array, USB state, log handle, and taskq. `usbser_port` tracks port mutex, parent state, log handle, DSD copy, port number/state/activity/flags, state/activity/carrier CVs, write-queue byte count, read/write worker threads, `tty_common`, flow-control char, and delay/break timeout.

The port-state diagram documents tty vs dial-out open behavior, carrier-detect blocking, dial-out overtaking, suspended/disconnected handling, and close/open race avoidance.

Minor numbers reserve low bits for port, high bits for instance, and the top bit for dial-out (`OUTLINE`).
