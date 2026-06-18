# File Research: sources/os/bsd/netbsd-src/sys/sys/swap.h

This header defines the public/userland ABI for NetBSD swap device reporting and control. Its central object is `struct swapent`, returned to userland for swap device information.

Key interface details:
- Includes `<sys/syslimits.h>` for `PATH_MAX`.
- `struct swapent` carries device id, flags, total blocks, blocks in use, priority, path, bad page count, and reserved padding.
- `__CTASSERT(sizeof(struct swapent) == 1184)` makes the structure size an explicit user ABI contract.
- Defines swap control operation codes: `SWAP_ON`, `SWAP_OFF`, `SWAP_NSWAP`, historical `SWAP_STATS*` variants, priority control, dump device selection/query, dump disable, and current `SWAP_STATS`.
- Defines swap device state flags: `SWF_INUSE`, `SWF_ENABLE`, `SWF_BUSY`, `SWF_FAKE`.

Research notes:
- This file is ABI-sensitive. Any field reorder, type change, or size change in `struct swapent` would break userland consumers.
- The multiple historical `SWAP_STATS*` commands show compatibility preservation across NetBSD releases.
- Filesystem/storage relevance is direct: this is the user-visible swap device accounting and control surface.
