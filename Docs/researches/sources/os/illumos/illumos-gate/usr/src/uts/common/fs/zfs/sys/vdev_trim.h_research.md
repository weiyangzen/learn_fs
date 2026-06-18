# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_trim.h

This header declares manual TRIM and autotrim control APIs for vdevs.

Core API surface:
- Tunable `zfs_trim_metaslab_skip` controls metaslab skipping behavior.
- `vdev_trim()` starts TRIM for a vdev with rate, partial, and secure flags.
- Stop/stop-all/stop-wait/restart helpers manage manual TRIM state.
- `vdev_autotrim()`, `vdev_autotrim_stop_all()`, `vdev_autotrim_stop_wait()`, and `vdev_autotrim_restart()` manage background autotrim.

Risk-sensitive invariants:
- Manual TRIM and autotrim have separate thread/lock/CV state in `struct vdev`.
- Secure and partial TRIM flags change device commands and accounting semantics.
