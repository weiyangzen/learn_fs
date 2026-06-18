# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zfs.conf

Registers the ZFS kernel module as a pseudo-device with `name="zfs" parent="pseudo";`. This is the driver/module configuration stub used by illumos packaging and module loading, not filesystem behavior logic.

The file is otherwise license/header metadata. Its operational effect is limited to making the ZFS module appear under the pseudo device parent so the kernel can attach the ZFS subsystem through normal module configuration paths.

There are no tunables, functions, state machines, or cross-file logic in this file.
