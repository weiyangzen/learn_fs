# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/vm.h

## Role

`vm.h` is a small umbrella header for VM subsystem declarations. It includes VM parameter, VM system, and system macro headers, then exposes a few kernel VM entry points.

## Key Interfaces

For kernel builds, it includes `sys/vnode.h` and declares:
- `setupclock()`
- `pageout()`
- `cv_signal_pageout()`
- `queue_io_request(struct vnode *, u_offset_t)`

It also declares `memavail_lock` and `memavail_cv`.

The `WAKE_PAGEOUT_SCANNER(tag)` macro emits a DTrace probe named from the supplied tag and broadcasts on `proc_pageout->p_cv`.

## Research Notes

This file is a coordination header for pageout and memory-availability signaling. The DTrace token-pasting macro requires compile-time probe tag names.
