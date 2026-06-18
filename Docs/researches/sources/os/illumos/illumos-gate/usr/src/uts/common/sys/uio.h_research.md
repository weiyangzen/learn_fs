# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/uio.h

## Purpose
Scatter/gather I/O vector and kernel `uio` definitions for read/write movement, async direct-copy support, and extended zero-copy I/O.

## Main Interfaces
- Defines `iovec_t`/`struct iovec` and `struct iovec32`.
- Defines `uio_seg_t` address-space enum values `UIO_USERSPACE`, `UIO_SYSSPACE`, and `UIO_USERISPACE`.
- Defines `uio_t` with iovec pointer/count, offset, segment flag, residual count, file limit, and flags.
- Defines `uioa_page_t`, `uioa_t`, `xuio_t`, `xuio_type`, and XUIO zero-copy helper macros.
- Defines `uio_rw_t` with `UIO_READ` and `UIO_WRITE`.
- Defines `UIO_COPY_DEFAULT`, `UIO_COPY_CACHED`, `UIO_ASYNC`, and `UIO_XUIO`.
- Defines `uioasync_t` global capability state.
- Kernel declarations include `uiomove`, `uio_prefaultpages`, `uiocopy`, `ureadc`, `uwritec`, `uioskip`, `uiodup`, `uioamove`, `uioainit`, and `uioafini`.
- User declarations expose `readv`, `writev`, `preadv`, `pwritev`, and large-file `preadv64`/`pwritev64` variants.

## Dependencies And Relationships
Includes `sys/feature_tests.h` and `sys/types.h`. Used by VFS, device drivers, filesystems, and libc scatter/gather APIs.

## Research Notes
The header is a key boundary between user scatter/gather ABI and kernel data movement. Large-file remapping and `uio_offset` layout are compilation-environment dependent.
