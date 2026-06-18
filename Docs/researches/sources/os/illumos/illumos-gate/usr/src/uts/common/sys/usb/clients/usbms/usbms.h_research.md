# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/usbms/usbms.h

USB mouse STREAMS module state header. It defines mouse sample/buffer structures, parsed HID input descriptor metadata, full per-instance state, button mapping constants, jitter/speed filtering settings, transparent ioctl state, and debug masks.

`usbms_state_t` includes read/write queues, open/qwait flags, pending ioctl message, `ms_softc`, previous button state, HID parser handle, jitter threshold/timeouts, speed limit/law counters, button/wheel counts, report ID and logical maxima, screen resolution, absolute-report flag, parsed input descriptor, and mouse sample buffer.

Macros include absolute value, byte clipping to signed 7-bit mouse deltas, default/max button counts, input parser states, default screen resolution, USB-to-Type-5 button encodings, and default jitter/speed/buffer tunables.
