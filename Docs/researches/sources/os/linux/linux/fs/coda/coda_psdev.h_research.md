# File Research: sources/os/linux/linux/fs/coda/coda_psdev.h

Coda pseudo-device and Venus upcall interface header.

Defines:
- `CODA_PSDEV_MAJOR` as 67.
- `MAX_CODADEVS` as 5.
- `struct upc_req`: one kernel-to-Venus request with list linkage, data pointer, flags, input/output sizes, opcode, unique ID, and waitqueue.
- Request flags: async, read, write, abort.
- `struct venus_comm`: per-communication-channel sequence, Venus waitqueue, pending/processing lists, in-use flag, superblock pointer, and mutex.
- `coda_vcp()`: superblock to `venus_comm`.

Declares Venus operations:
- Root FID, getattr/setattr, lookup, open/close, mkdir/create/rmdir/remove, readlink, rename, link/symlink, access, pioctl, fsync, statfs, access intent.
- `coda_downcall()` for Venus-to-kernel invalidation/results.
- Global `coda_comms[]`.

Role:
- Defines the internal kernel/userspace protocol surface between Coda VFS code and Venus cache manager.
