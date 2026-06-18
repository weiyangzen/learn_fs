# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhci.h

UHCI hardware and descriptor-layout header. It defines UHCI controller registers (`hc_regs_t`), command/status/interrupt/port bits, MMIO accessor wrappers, queue heads, transfer descriptors, TD field extract/set macros, frame-list sizing, pointer masks, TD status/PID constants, and bandwidth constants.

The descriptor structures include both hardware-controlled fields and software-only linkage used for queues, outstanding TD tracking, transfer-wrapper association, and isochronous scheduling.

The file sets UHCI-specific limits: 1024 frame-list entries, 64 interrupt QH lists, 16-byte QH/TD alignment, maximum bulk TDs per transfer, 1024 isochronous frames, and low-speed/full-speed bandwidth assumptions.

It is the hardware contract consumed by `uhcid.h`, `uhciutil.h`, and transfer scheduling code. Correct field packing and bit operations are essential because UHCI uses compact, bitfield-heavy TD words.
