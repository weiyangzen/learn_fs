# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/swapnode.h

This header declares swapfs global reservation values and vnode interfaces.

Globals:
- `swapfs_minfree` is the amount of available resident memory unavailable to swapfs.
- `swapfs_desfree` is another free-memory threshold.
- `swapfs_reserve` is unavailable for swap reservation by non-privileged processes.

Interfaces:
- `swap_vnodeops` exposes swapfs vnode operations.
- `swapfs_getvp(ulong_t)` returns a swapfs vnode.

Debugging:
- Under `SWAPFS_DEBUG`, exposes `swapfs_debug`, `SWAPFS_PRINT`, and debug bit categories for subroutines, vnode ops, VFS ops, page creation, and putpage.
- Without debug, print macro compiles away.

Dependencies and relationships:
- Swapfs is a vnode-backed pseudo filesystem for anonymous/swap reservations.
- This header is intentionally small and mostly exports globals to swapfs implementation units.
