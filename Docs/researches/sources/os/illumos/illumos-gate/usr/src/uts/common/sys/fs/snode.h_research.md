# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/snode.h

This header defines specfs special-file snode state, flags, and kernel interfaces.

Purpose:
- An snode represents an active special file.
- Filesystems that support special files convert normal vnodes to special vnodes with `specvp()`.
- `s_commonvp` points to a common vnode used for device data caching, preventing cache aliasing across multiple filesystem entries for the same device.
- Kernel-created snodes may have no real vnode and use their own vnode as common vnode.

Node model:
- `snode` stores stable-table link, associated vnode, real vnode, common vnode, device number, devinfo pointer, read-ahead offset, sync list link, device policy, block-device size, flags, fsid, times, open count, mapping count, lock, and condition variable.
- Comments identify which fields are protected by `stable_lock`, `spec_syncbusy`, or `s_lock`.

Flags:
- Update/access/change time bits, private open, 64-bit/any-offset support, open/close serialization, waiter, clone/self-clone, needs close, device association, size valid, multiplexed stream, no flush, closing, and fenced for I/O retire.

Kernel conversions:
- `VTOS`, `VTOCS`, and `STOV` map between vnode, common snode, and vnode.

Kernel API:
- Specfs VFS/vnode operation accessors, snode cache, common vnode creation/lookup, controlling terminal creation, delete/mark, init, device close, putpage, segmap, devfs-associated specvp creation, devinfo association/hold, sync, snode walk, open-count lookup, clone checks, fencing/unfencing, and size invalidation.
- Async putpage globals are declared.

Size constants:
- `UNKNOWN_SIZE` is `MAXOFFSET_T` for devices without size properties.
- On 32-bit kernels, `SPEC_MAXOFFSET_T` limits block-driver offsets due to 32-bit `daddr_t`.

Hashing:
- Stable table size is 256 and hashes by major+minor.
- Stable table and locks are declared.

Dependencies and relationships:
- Bridges VFS special-file entries, device driver opens/closes, devinfo association, page cache aliasing, and device retirement fencing.
