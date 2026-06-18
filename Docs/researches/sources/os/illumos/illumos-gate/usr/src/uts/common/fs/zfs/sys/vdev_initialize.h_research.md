# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_initialize.h

This header declares vdev initialization control APIs. Initialization writes across allocatable space so later reads avoid exposure to stale media state.

Public API surface:
- `vdev_initialize()` starts initialization for a vdev.
- `vdev_initialize_stop()` stops one vdev toward a target state and records it in a caller list.
- `vdev_initialize_stop_all()` applies a target state to a subtree.
- `vdev_initialize_stop_wait()` waits for stop completion for a SPA/list.
- `vdev_initialize_restart()` restarts initialization.

Risk-sensitive invariants:
- The actual progress fields and thread/CV state live in `struct vdev`.
- Stop/restart operations must coordinate with spa async tasks and vdev lifecycle.
