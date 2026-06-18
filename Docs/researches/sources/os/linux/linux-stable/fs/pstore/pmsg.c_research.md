# File Research: sources/os/linux/linux-stable/fs/pstore/pmsg.c

## Summary
Implements `/dev/pmsg0`, a character device for userspace messages persisted through pstore.

## Main Responsibilities
- Register a dynamic char device major named `pmsg`.
- Create a device class and `/dev/pmsg0` node with write-only permissions.
- Convert user writes into `PSTORE_TYPE_PMSG` records.
- Serialize writes with a mutex.

## Key Interfaces
- `pstore_register_pmsg()` creates the char device and class.
- `pstore_unregister_pmsg()` destroys them.
- `write_pmsg()` validates user memory, initializes a record, and calls `psinfo->write_user()`.

## Important Behavior
The write path first calls `access_ok()` outside the mutex to fault-check the range as much as possible, then serializes actual backend writes under `pmsg_lock`. It returns the backend result when nonzero, otherwise the byte count.

## Cross-File Interactions
`platform.c` registers this frontend when the backend advertises `PSTORE_FLAGS_PMSG`. `ram.c` and `zone.c` implement pmsg storage paths.
