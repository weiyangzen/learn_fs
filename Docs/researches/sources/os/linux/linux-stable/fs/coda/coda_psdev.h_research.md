# File Research: sources/os/linux/linux-stable/fs/coda/coda_psdev.h

## Purpose
Defines the Coda pseudo-device communication structures and Venus upcall/downcall API declarations.

## Main Contents
- Device constants: `CODA_PSDEV_MAJOR`, `MAX_CODADEVS`.
- `struct upc_req`: queued request data, flags, sizes, opcode, unique ID, and waitqueue.
- Request flags: async, read, write, abort.
- `struct venus_comm`: sequence number, Venus waitqueue, pending/processing lists, in-use flag, superblock pointer, and mutex.
- `coda_vcp()` helper to access `venus_comm` from a superblock.
- Prototypes for all Venus operations used by VFS paths: rootfid, getattr/setattr, lookup, open/close, create/mkdir/remove/rmdir/rename/link/symlink, readlink, access, pioctl, fsync, statfs, access intents, and downcalls.
- Extern `coda_comms[]`.

## Integration Points
Shared by Coda psdev/upcall implementation and VFS operation files. It defines the kernel-to-Venus RPC boundary.

## Risks And Review Focus
- Request size fields note a small maximum; upcall encoding/decoding must enforce bounds.
- Queue ownership and abort semantics depend on `venus_comm` locking and waitqueue discipline in implementation files.
