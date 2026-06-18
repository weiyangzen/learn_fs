# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhcireg.h

xHCI register and bitfield definition header, under a permissive BSD-style license from upstream authors plus Joyent copyright. It defines PCI config offsets, capability registers, operational registers, runtime registers, doorbells, extended capability IDs, legacy ownership bits, supported protocol fields, slot and endpoint context field macros, TRB field macros, TRB types, and completion codes.

The header is pure constants/macros and has no driver state. It is used by `xhci.h` and implementation files to parse controller capabilities, program MMIO registers, construct contexts, construct TRBs, decode events, and handle completion status.

Important correctness areas are field shift/mask helpers, port-status write semantics, event-ring register layout, doorbell targeting, endpoint type encodings, TRB cycle/type/slot/endpoint fields, and completion-code mapping.
