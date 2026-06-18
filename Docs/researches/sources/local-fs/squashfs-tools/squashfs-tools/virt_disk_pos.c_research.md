# File Research: sources/local-fs/squashfs-tools/squashfs-tools/virt_disk_pos.c

Thread-safe virtual-to-disk position map for `mksquashfs` write-position tracking.

Key state:
- Global positions `vpos`, `dpos`, and `marked_vpos`.
- Static hash table `vd_hashtable[VIRT_DISK_HASH_SIZE]`.
- Mutex/condition pair for coordinating waiters on virtual-position mappings.

Functions:
- `add_virt_disk(virt, disk)` inserts a virtual-to-real disk mapping and signals a waiter if it is waiting for that virtual offset.
- `get_virt_disk(virt)` returns an existing mapping or aborts as an internal bug.
- `get_virt_disk_wait(virt)` blocks until the requested virtual mapping is inserted, then returns the disk position.

The table is append-only; there is no deletion path.
