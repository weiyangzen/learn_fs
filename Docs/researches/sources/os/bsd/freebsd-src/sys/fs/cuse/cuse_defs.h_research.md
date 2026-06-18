# File Research: sources/os/bsd/freebsd-src/sys/fs/cuse/cuse_defs.h

Read completely: 87 lines.

Purpose: defines public CUSE protocol constants shared by CUSE kernel and userland code.

Key definitions:
- `CUSE_VERSION` is `0x000125`.
- Negative `CUSE_ERR_*` values represent server-returned errors such as busy, would-block, invalid, no memory, fault, signal, other, not loaded, and no device.
- `CUSE_POLL_*` defines read/write/error readiness bits.
- `CUSE_FFLAG_*` maps open and operation flags, including read, write, nonblock, and 32-bit compat peer.
- `CUSE_CMD_*` enumerates command types: open, close, read, write, ioctl, poll, signal, sync.
- `CUSE_MAKE_ID()` and `CUSE_ID_MASK` build device-unit allocation namespaces.
- Named ID namespaces exist for default, webcamd, Sundtek, cx88, and uhidd users.

Research notes:
- This header is protocol ABI rather than implementation.
- Command and error constants are consumed directly by `cuse.c`.
