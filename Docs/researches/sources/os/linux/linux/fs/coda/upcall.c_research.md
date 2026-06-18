# File Research: sources/os/linux/linux/fs/coda/upcall.c

## Purpose
Implements the Coda kernel-to-Venus upcall wrappers, asynchronous/synchronous request transport, signal handling around Venus waits, pioctl marshalling, statfs/access-intent support, and Venus downcall invalidation handling.

## Main Elements
- Request allocation: `alloc_upcall()` fills opcode, pid, process group, and uid in a union request buffer.
- Venus operation wrappers: `venus_rootfid()`, `getattr()`, `setattr()`, `lookup()`, `open()`, `close()`, `mkdir()`, `rename()`, `create()`, `rmdir()`, `remove()`, `readlink()`, `link()`, `symlink()`, `fsync()`, `access()`, `pioctl()`, `statfs()`, and `access_intent()`.
- Variable-size payloads: lookup/create/remove/link/symlink/rename/pioctl build offset-based string or data payloads expected by the Coda userspace protocol.
- Upcall core: `coda_upcall()` assigns unique IDs, queues requests on `vc_pending`, wakes Venus, waits for replies when synchronous, maps Venus result codes to Linux errors, and sends `CODA_SIGNAL` async notifications on interrupted already-read requests.
- Signal policy: `coda_waitfor_upcall()` blocks most signals initially, allows interruption after `coda_timeout` for interruptible operations, and keeps close/store/access-intent/release harder to interrupt.
- Downcalls: `coda_downcall()` validates downcall payload sizes and handles cache invalidations or fid replacement for `CODA_FLUSH`, `PURGEUSER`, `ZAPDIR`, `ZAPFILE`, `PURGEFID`, and `REPLACE`.

## Dependencies And Integration
This is the main Coda protocol layer between VFS code and the Venus daemon. It uses `venus_comm` queues serviced by `psdev.c`, Coda dentry/inode cache helpers, fid-to-inode lookup, VFS dcache pruning, and exported protocol structs from `<linux/coda.h>`.

## Risk Notes
Protocol marshalling depends on exact union sizes, offsets, NUL termination, and Coda ABI command-size adjustments. Interrupted upcalls have subtle state transitions depending on whether Venus already read the request. Downcalls may invalidate dentries/inodes concurrently with VFS operations, so payload validation and locking around `vc_sb` are important.
