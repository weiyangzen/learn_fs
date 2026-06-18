# File Research: sources/os/plan9/plan9/sys/src/9/port/usbehci.c

## Role

Implements the USB 2.0 EHCI host-controller backend for the common Plan 9 USB layer. It supports control, bulk, interrupt, and isochronous endpoints, root-port control, scheduling, interrupt handling, and debug dumps.

## Main Data

The file defines software and hardware descriptors: `Qh` queue heads, `Td` queue transfer descriptors, high-speed `Itd`, split/full-speed `Sitd`, `Qio` endpoint-direction I/O state, `Ctlio` control request state, `Isoio` isochronous stream state, and `Qtree` periodic interrupt scheduling. `Edpool` allocates aligned descriptor unions from `xspanalloc`.

## Control Flow

`ehcimeminit` allocates the frame list, initializes the asynchronous QH ring, and builds the periodic QH tree. `init` enables EHCI interrupts, periodic and asynchronous schedules, runs the controller, routes ports, and powers ports.

`epopen` allocates endpoint-specific state and schedules QHs or ISO descriptors. `epread`/`epwrite` dispatch by transfer type. Non-ISO I/O builds QTD chains with `epgettd`, links them into the QH, waits in `epiowait`, handles missing interrupts through polling, copies data back, and frees QTDs. Control transfers are split into setup, data, and status phases. ISO I/O uses ITDs for high-speed and SITDs for full-speed split transactions, with circular frame windows and wakeups from interrupt processing.

`ehciintr` acknowledges controller status, processes ISO descriptors, periodic interrupt QHs, and asynchronous QHs. Port methods enable, reset, hand low/full-speed ownership to companion controllers, and return root-hub-compatible status.

## Dependencies

Depends on `usb.h`, EHCI register definitions in `portusbehci.h`/`usbehci.h`, uncached/aligned memory helpers, cache coherence primitives, Plan 9 locks, timers, sleeps, and controller `Ctlr` fields supplied by platform glue.

## Risks

The file documents known issues: excess delays/interrupt locks, incomplete per-frame bandwidth admission, polling required for some controllers, and no power-overrun warning. ISO sample packing is explicitly imperfect. Several paths panic on internal state corruption. Control read buffering has a `BUG for big transfers`. Correctness relies on descriptor alignment, `coherence()` placement, frame-list pointer manipulation, and careful close/cancel synchronization.
