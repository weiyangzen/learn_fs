# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcitgt.h

UHCI shared internal prototype header for target-side scheduling and cleanup helpers. It declares queue-head allocation/state lookup, insertion of control, bulk, interrupt, and isochronous TDs, QH insertion/removal, active-bit modification, bandwidth allocation/deallocation, TD/TW removal, isochronous receive polling, data-toggle save, root-hub helpers, callbacks, and periodic IN resource allocation.

This header ties together UHCI transfer construction, endpoint scheduling, bandwidth accounting, root-hub behavior, and callback completion paths.

It contains no structures beyond prototypes; its value is as an internal linkage contract among UHCI implementation files.
