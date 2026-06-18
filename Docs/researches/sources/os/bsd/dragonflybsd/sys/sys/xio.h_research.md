# File Research: sources/os/bsd/dragonflybsd/sys/sys/xio.h

## Summary
Kernel page-list data representation for I/O and mapping operations.

## Main Responsibilities
- Defines `struct xio` with page list, page count, byte offset, byte count, flags, error, and internal page-pointer storage sized from `MAXPHYS`.
- Defines read/write/VM-linear flags.
- Declares initialization, release, uio-copy, user/kernel copy-in/out helpers.
- Provides inline remaining-byte and KVA-offset helpers.

## Important Behavior
XIO represents a byte range over pages but does not track in-progress I/O. Copy routines do not mutate the XIO; callers track offsets.

## Risks
Offsets are relative to the represented dataset, not the first page. Confusing `uoffset`, `xio_offset`, and KVA offset can copy the wrong byte range.
