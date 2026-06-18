# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_onexit.h

Declares per-control-device on-exit callback management used to register cleanup actions tied to a ZFS device fd/minor.

Key elements:
- Kernel `zfs_onexit_t` contains a mutex and action list.
- `zfs_onexit_action_node_t` stores callback function and opaque data.
- Declares init/destroy plus fd hold/release, callback add/delete, and callback data lookup.

Main dependencies and interactions:
- Includes `zfs_context.h`.
- Related to `zfs_ioctl.h` soft state, where control device minors can point to `zfs_onexit_t`.

Implementation notes:
- Public helper prototypes are outside `_KERNEL`, indicating user/kernel shared declarations for ioctl support.
