# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_intr.h

EHCI interrupt-handling prototypes. It declares handlers for USB errors, frame-list rollover, endpoint reclamation, active QTD traversal, QTD error checking, generic error handling, and per-transfer-type QTD completion handling for control, bulk, and interrupt transfers.

The prototypes show the interrupt layer operates over `ehci_state_t`, pipe-private state, transfer wrappers, QTDs, completion reasons, and opaque callback data.
