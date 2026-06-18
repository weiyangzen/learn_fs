# File Research: sources/os/linux/linux/fs/pstore/pmsg.c

## Role

Implements the `/dev/pmsg0` userspace persistent message frontend.

## Key Functions

- `write_pmsg()` validates nonzero writes, initializes a `PSTORE_TYPE_PMSG` record, checks userspace access, serializes writes with `pmsg_lock`, and calls backend `write_user()`.
- `pstore_register_pmsg()` registers a dynamic char device major, creates a `pmsg` class, sets device node mode to write-only group/owner style `0220`, and creates `pmsg0`.
- `pstore_unregister_pmsg()` destroys the device, class, and char device.

## Research Notes

The frontend never buffers user data itself when the backend supports `write_user()`. The core platform layer supplies a compatibility implementation for backends without native user-copy support.
