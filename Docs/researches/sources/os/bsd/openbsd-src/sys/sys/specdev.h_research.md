# File Research: sources/os/bsd/openbsd-src/sys/sys/specdev.h

Special-device vnode metadata and operation declarations.

This header defines `struct specinfo`, the vnode-attached metadata for block and character special devices. It records hash-chain membership, special-device list linkage, mountpoint, raw device number, advisory-lock state, last read block, and clone-device parent/bitmap state. `struct cloneinfo` records a cloned vnode and original private data.

It provides shorthand macros mapping vnode fields to `v_specinfo` members, clone encoding constants, special-device hash constants, the global `speclisth` table, and prototypes for `spec_*` vnode operations such as open, close, read, write, ioctl, strategy, fsync, inactive, pathconf, and advisory lock.

Filesystem/storage relevance: high. Special vnodes are the bridge between VFS and device drivers, including raw/block storage devices used for mounted filesystems, swap, and direct disk access.
