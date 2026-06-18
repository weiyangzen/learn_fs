# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_file.h

This header defines file-backed vdev type-specific state.

Core definition:
- `vdev_file_t` contains the backing file `vnode_t *vf_vnode`.

Risk-sensitive invariants:
- File vdev operations must manage vnode lifetime outside this struct.
- The header intentionally contains no public operations; it is type-specific data consumed by vdev file code.
