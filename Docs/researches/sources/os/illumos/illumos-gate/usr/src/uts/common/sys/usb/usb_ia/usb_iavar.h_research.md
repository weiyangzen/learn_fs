# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/usb_ia/usb_iavar.h

USB Interface Association driver private state header. It defines `usb_ia_t`, init-state flags, child event flags, and debug masks.

`usb_ia_t` tracks instance/init state, mutex, devinfo, common USB power state, device state, first interface, number of grouped interfaces, per-child event registration, child devinfo array, child-list length, logging handle, USB registration data, and NDI event handle.

This driver groups multiple USB interfaces that belong to an interface association. Its state is smaller than `usb_mid_t` because it focuses on an associated interface range rather than generic multi-interface device management.

Concurrency is guarded by `ia_mutex`, with annotations for stable unlocked fields and shared `usb_common_power_t`.
