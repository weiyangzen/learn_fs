# File Research: sources/virtualization/libguestfs/daemon/blockdev.c

Centralizes wrappers around the external `blockdev` command.

Key points:
- `call_blockdev` runs `udev_settle()` before every blockdev invocation to avoid udev/blkid races after prior writes.
- Handles commands with optional integer arguments and optional numeric stdout parsing.
- Exposes set/get read-only, sector size, block size, total sectors, byte size, flush buffers, and reread partition table.
- `do_blockdev_setbsz` is intentionally a no-op due to historical bug compatibility.
- `do_blockdev_setra` rejects negative readahead sectors.
