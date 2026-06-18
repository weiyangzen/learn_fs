# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_mid/usb_midvar.h

USB multi-interface driver private state header. It defines `usb_mid_t`, minor-number encoding macros for ugen support, init-state flags, child event flags, and debug masks.

`usb_mid_t` tracks instance/init state, ugen open count, mutex, devinfo, common power state, USBA device, softstate/device state, interface count, per-child event registration, child interface numbers, child devinfo array, removal/attach counters, logging, USB registration data, NDI event handle, and ugen handle.

This header supports devices whose multiple interfaces are split into child nodes. It handles both normal child event tracking and generic user-level access through ugen minor allocation.

Concurrency uses `mi_mutex`; Warlock annotations identify stable data readable without the lock.
