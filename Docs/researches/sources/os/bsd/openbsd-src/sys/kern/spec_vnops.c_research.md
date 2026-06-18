# File Research: sources/os/bsd/openbsd-src/sys/kern/spec_vnops.c

Read completely: 746 lines.

Implements vnode operations for special device files (`VCHR` and `VBLK`) in OpenBSD. It connects VFS operations to character/block device switch tables, enforces securelevel and mount restrictions, handles buffered block-device I/O, fsync/invalidation, advisory locks, pathconf, kqueue filters, and cloned character devices.

Vops table:
- `spec_vops` maps generic unsupported filesystem operations to badop/generic handlers and implements open, close, access, getattr, setattr, read, write, ioctl, kqfilter, fsync, inactive, strategy, print, pathconf, advlock, and bwrite behavior for special vnodes.
- `speclisth[SPECHSZ]` is the special vnode hash/list storage.

Open and close:
- `spec_open()` rejects opens from `MNT_NODEV` mounts, validates major numbers, enforces securelevel restrictions on writing disk devices and `/dev/mem`/`/dev/kmem`, prevents writing mounted corresponding block devices, marks tty vnodes, delegates clone devices to `spec_open_clone()`, and calls the relevant character or block `d_open`.
- `spec_close()` handles controlling-terminal vnode references, clone-device bookkeeping, last-reference behavior, block-device buffer invalidation via `vinvalbuf()`, forced close cases during vnode cleaning, and calls the relevant device `d_close`.
- Cloned character devices clear their bitmap slot and release their parent vnode after successful close.

Read/write and strategy:
- `spec_read()` dispatches character reads directly to `cdevsw[].d_read()` with the vnode unlocked. For block devices it rejects negative offsets, chooses an I/O size from partition FFS fragment metadata when available, performs buffered reads with simple read-ahead using `v_lastr`, and copies data with `uiomove()`.
- `spec_write()` dispatches character writes to `cdevsw[].d_write()` with the vnode unlocked. For block devices it reads the containing block, copies user data into the buffer, and writes full blocks asynchronously or delayed-writes partial blocks.
- `spec_strategy()` forwards buffer I/O to the block device strategy routine.

Device operations and metadata:
- `spec_ioctl()` dispatches to character or block `d_ioctl`.
- `spec_kqfilter()` uses a device-provided character-device kqfilter when present, otherwise supports poll/select fallback through `seltrue_kqfilter()` for non-character cases.
- `spec_fsync()` flushes dirty buffers for block devices and waits for completion when requested.
- `spec_inactive()` simply unlocks the vnode.
- `spec_getattr()`, `spec_setattr()`, and `spec_access()` operate only on clone vnodes and forward metadata/access operations to the parent special vnode.
- `spec_print()` emits debug vnode information when debug/diagnostic flags are enabled.
- `spec_pathconf()` returns POSIX limits relevant to special devices.
- `spec_advlock()` delegates byte-range advisory locking to `lf_advlock()` over `v_speclockf`.

Clone devices:
- `spec_open_clone()` allocates a free clone minor slot from the parent bitmap, creates a new character device vnode with the encoded clone minor, opens the cloned device, marks the clone vnode with `VCLONE`, stores parent linkage in `v_specparent`, marks the parent `VCLONED`, and installs `struct cloneinfo` in the parent vnode data.
- Failure paths clear the allocated bitmap slot and release the clone vnode.

Filesystem relevance:
- This file is the VFS-to-device bridge for special files. Block device reads/writes use the buffer cache and partition geometry, while open/close rules protect mounted filesystems and securelevel-sensitive devices.
