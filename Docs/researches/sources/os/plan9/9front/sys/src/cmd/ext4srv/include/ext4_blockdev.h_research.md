# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/include/ext4_blockdev.h

Block device abstraction header. It defines the physical device callback interface, logical block device state, static initialization macro, and cached/direct/block-byte IO APIs.

Key behavior:
- `ext4_blockdev_iface` supplies open, read, write, close, optional lock/unlock callbacks, physical block geometry, physical scratch buffer, reference count, IO counters, and user pointer.
- `ext4_blockdev` stores partition offset/size, bound cache, logical block size/count, writeback reference count, owning filesystem, and journal pointer.
- `EXT4_BLOCKDEV_STATIC_INSTANCE` creates static interface and device objects with a physical scratch buffer.
- Declares lifecycle, cache binding, buffer flush, LBA flush, logical block size setup, cached block get/set, direct block IO, byte-range IO, cache flush, and writeback toggle functions.

Notable dependencies:
- Includes `ext4_bcache.h`.
- Implemented by `ext4_blockdev.c`; used by every storage-facing module.

Research notes:
- `#pragma incomplete struct ext4_blockdev` reflects Plan 9 C conventions.
- The device layer supports partitions by combining callback-level physical geometry with `part_offset` and `part_size`.
