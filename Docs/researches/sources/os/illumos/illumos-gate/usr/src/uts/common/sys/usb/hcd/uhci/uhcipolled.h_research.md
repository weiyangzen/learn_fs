# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcipolled.h

UHCI polled-mode header. It defines raw buffer sizing, input/output mode flags, in-use flags, low-speed keyboard capacity constant, and `uhci_polled_t`.

The polled state stores the controller, pipe handle, interrupt QH, polling TD, input buffer, polled flags, and nested-entry counter. Warlock annotations state that key fields are only accessed in polled mode.

It declares polled input/output HCDI entry points and a few helper routines used during init/fini paths, including state lookup, queue-head allocation, and transfer-wrapper freeing.

The file supports keyboard/console access when normal interrupt scheduling cannot be used.
