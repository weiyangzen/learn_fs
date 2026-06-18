# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhciutil.h

UHCI utility and HCDI prototype header. It declares public HCDI pipe operations, transfer-size queries, frame-number and isochronous-packet queries, root-hub request handling, TD completion handlers, submitted-TD processing, DMA/pool/controller/register setup and teardown, bandwidth handling, transfer-wrapper lifecycle, timeout handling, transfer insertion helpers, isochronous helpers, kstat creation/destruction, and small arithmetic helpers.

This is the broadest UHCI prototype surface and is consumed across attach/init, HCDI, control/bulk/intr/isoc transfer, interrupt, timeout, and statistics code.

It separates function declarations from the descriptor/state definitions in `uhci.h` and `uhcid.h`, keeping the driver’s internal compilation units aligned on shared entry points.
