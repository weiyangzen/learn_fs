# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_xfer.h

EHCI transfer-management prototypes. It declares QH allocation/insertion/removal/deallocation/address conversion, control/bulk/interrupt resource allocation and request insertion, periodic polling start/stop, QTD insertion/removal/deallocation/address conversion, transfer-wrapper TD allocation/timer/deallocation/free-DMA helpers, interrupt IN resource management, pipe cleanup, transfer completion checks, data-toggle restoration, outstanding-request handling, client periodic callback dispatch, generic HCDI callbacks, and clear-TT-buffer handling.

The API shows the transfer layer is organized around QHs, QTDs, transfer wrappers, pipe-private state, and USBA request types for control, bulk, interrupt, and periodic polling.
