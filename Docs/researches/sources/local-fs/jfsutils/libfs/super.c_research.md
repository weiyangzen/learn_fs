# File Research: sources/local-fs/jfsutils/libfs/super.c

This file provides shared superblock and log-superblock validation and I/O helpers.

Main functions:
- `inrange()` tests whether `num` is one of the power-of-two multiples from `low` through `high`.
- `validate_sizes()` currently validates that allocation group size is at least one dmap (`1 << L2BPERDMAP`).
- `ujfs_validate_super()` checks JFS magic, supported version, and size validity.
- `ujfs_put_superblk()` writes primary or secondary aggregate superblock space, zero-padding the full `SIZE_OF_SUPER` region and endian-swapping before disk I/O.
- `ujfs_get_superblk()` reads primary or secondary aggregate superblock and endian-swaps into host order.
- `ujfs_validate_logsuper()` checks log magic and exact log version.
- `ujfs_put_logsuper()` writes the log superblock at log page 1.
- `ujfs_get_logsuper()` reads the log superblock from log page 1.

Integration points:
- Used by mkfs/fsck/log utilities needing common superblock access.
- Disk I/O is through `ujfs_rw_diskblocks()`.
- Error returns use `LIBFS_*` constants from `libjufs.h`.

Notes:
- `ujfs_get_superblk()` swaps the buffer before checking `rc`; if the read failed, it swaps untrusted local contents before returning the error.
- Logsuper helpers operate at `LOGPSIZE`, matching log page 1 for external log devices.
