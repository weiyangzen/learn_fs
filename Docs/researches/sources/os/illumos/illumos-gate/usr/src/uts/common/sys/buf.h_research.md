# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/buf.h

`buf.h` defines the classic block I/O buffer header `buf_t`, including device/block identity, byte counts, mapped data union, page I/O fields, vnode association, semaphores, I/O callback, private driver data, and file/offset association. It also defines buffer hash heads, delayed-write heads, and buffer-cache kstats.

The file is the shared declaration point for many buffer flags (`B_BUSY`, `B_DONE`, `B_ERROR`, `B_PAGEIO`, delayed-write/cache/invalidation/retry/failfast flags), list-manipulation macros, and kernel buffer-cache operations (`bread`, `getblk`, `bwrite`, `bdwrite`, `brelse`, `iodone`, `bioerror`, `pageio_setup`, `bioclone`, mapping/copy helpers, flush/invalidate helpers). It is central to filesystem and block I/O paths.
