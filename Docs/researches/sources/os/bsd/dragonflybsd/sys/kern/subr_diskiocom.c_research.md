# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_diskiocom.c

Disk DMSG/kdmsg bridge exposing a local raw disk as a remote block peer and executing remote block operations against the raw device.

Key responsibilities:
- Initializes and tears down per-disk `kdmsg_iocom` state with autoconnect, autorxspan, and autotxspan enabled.
- Handles `DIOCRECLUSTER` by reconnecting the disk iocom over a provided file descriptor.
- Publishes block media size, block size, peer labels, and PFS labels derived from hostname, device name, and serial number.
- Dispatches received DMSG transactions for block open, read, write, flush, and free-block commands.
- Converts remote block commands into kernel pbuf/BIO operations against `dp->d_rawdev`.
- Replies asynchronously from `diskiodone()` with DMSG error codes and read data in auxiliary payloads.

Important behavior:
- Non-transaction root-state messages are rejected except for limited debug message handling.
- `DMSG_BLK_OPEN` tracks per-transaction read/write open counts and closes raw-device references when the transaction is deleted.
- Writes with short auxiliary data zero-fill the remainder of the requested block range.
- Reads copy pbuf data into a newly allocated DMSG auxiliary reply buffer.
- `blk_active` tracks active iocom BIOs and is exposed under `debug.blk_active`.

Dependencies:
- Depends on DragonFly DMSG/kdmsg, raw dev_ops, pbuf/BIO, proc0 credentials, file descriptor hold logic, and disk media info.

Notable risks:
- Explicit block close handling is disabled with `#if 0`; cleanup relies on transaction delete handling.
- Bounds and permission enforcement are delegated to the raw device strategy/open paths.
- Comments show `kdmsg_state_hold/drop` are disabled, so state lifetime safety depends on kdmsg transaction serialization.
