# File Research: sources/os/bsd/openbsd-src/sys/miscfs/fifofs/fifo.h

Purpose: Declares FIFO vnode operation prototypes when FIFO support is compiled in.

Key behavior:
- Exposes FIFO operation entry points for open, close, read, write, ioctl, kqfilter, inactive, reclaim, print, pathconf, advisory locking, and failed operations.
- Declares `fifo_printinfo()` for debug/diagnostic vnode printing.
- Contents are guarded by `#ifdef FIFO`.

Filesystem relevance:
- This header is the internal interface consumed by the FIFO vnode implementation and VFS configuration.
