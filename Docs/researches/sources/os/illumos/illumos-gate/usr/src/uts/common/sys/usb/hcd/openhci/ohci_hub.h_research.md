# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci_hub.h

OHCI root-hub private state header. It defines `ohci_root_hub_t`, which caches the hub descriptor, root-hub descriptor registers, hub/port status, per-port state, control and interrupt pipe handles, current requests, saved interrupt request, and interrupt-pipe timer.

It also defines OHCI root-hub port states: uninitialized, powered off, disconnected, disabled, enabled, and suspended. `OHCI_RH_POLL_TIME` sets the root-hub polling interval.

The file is consumed by the OHCI driver-private state in `ohcid.h` and root-hub request handling code. It translates hardware root-hub registers into USBA hub-class behavior.
