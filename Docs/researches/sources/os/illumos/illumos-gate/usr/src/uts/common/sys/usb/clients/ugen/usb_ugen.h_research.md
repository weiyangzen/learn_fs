# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/clients/ugen/usb_ugen.h

User-facing UGEN status and isochronous request ABI definitions. It enumerates endpoint last-command status values, including USB link errors, stalls, underruns/overruns, timeout, no bandwidth, disconnect/suspend, invalid/interrupted/no-resource requests, and isochronous polling failures.

It defines endpoint control flag `USB_EP_INTR_ONE_XFER`, device status values exposed through device-status minors, and isochronous packet/request header structures used between applications and ugen.

The isochronous ABI uses `ugen_isoc_pkt_descr_t` for per-packet requested length, actual length, and status, plus `ugen_isoc_req_head_t` with a flexible one-entry descriptor array pattern.
