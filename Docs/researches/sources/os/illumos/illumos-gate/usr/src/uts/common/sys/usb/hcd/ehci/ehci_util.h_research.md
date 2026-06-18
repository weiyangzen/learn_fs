# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_util.h

EHCI utility/init/deinit/bandwidth/miscellaneous function prototypes. It declares DMA attribute setup, pool allocation, DMA bind result decoding, register mapping, interrupt/mutex setup, controller initialization, HCDI ops allocation, cleanup, CPR suspend/resume, bandwidth allocation/deallocation, polling interval adjustment, state lookup, operational checks, soft reset, transfer attribute lookup, frame-number retrieval, SOF wait, scheduler toggling, debug printers, and kstat/stat helpers.

This header is the shared utility API used across EHCI attach/detach, scheduling, bandwidth management, and diagnostics.
