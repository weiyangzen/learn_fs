# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_hub.h

EHCI root hub state header. It defines `ehci_root_hub_t`, which stores the hub descriptor, companion controller count, per-port status/state arrays, control and interrupt pipe handles, current control/interrupt requests, saved client interrupt request, interrupt pending-status bitmap, and polling timer ID.

Port states cover uninitialized, powered off, disconnected, disabled, enabled, and suspended. Timing constants define root-hub polling interval, reset/suspend/resume waits, completion waits, and retry limits.
