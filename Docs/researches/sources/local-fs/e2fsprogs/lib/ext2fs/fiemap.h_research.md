# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fiemap.h

## Role

Local copy of Linux FIEMAP ioctl definitions used when system headers do not provide them.

## Main Contents

- Defines `struct fiemap_extent` and `struct fiemap`.
- Supplies Linux ioctl numbers for `FS_IOC_FIEMAP`, `EXT4_IOC_GETSTATE`, and `EXT4_IOC_GET_ES_CACHE` when missing.
- Defines FIEMAP request flags and extent flags.
- Adds ext4-specific cache/hole state constants.

## Dependencies

Relies on Linux-style `__u32` and `__u64` types supplied by surrounding ext2fs headers. Uses GCC diagnostic pragmas to tolerate zero-length array syntax.

## Risks / Notes

- This is ABI-facing data layout; changes must track kernel definitions carefully.
- `FIEMAP_FLAGS_COMPAT` excludes `FIEMAP_FLAG_CACHE`, so callers using cache requests need explicit handling.
