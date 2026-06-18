# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/llseek.c

Portable large-file seek wrapper exported as `ext2fs_llseek()`. On Linux it chooses between native `lseek`, `lseek64`, `llseek`, or the `_llseek` syscall depending on configure results.

If the kernel lacks llseek support, it falls back to regular `lseek` only when the requested offset fits in `off_t`; otherwise it returns `EINVAL`. Non-Linux platforms use `lseek64` when available or perform the same range check.

This file is foundational for raw image/device code that needs offsets beyond 2 GiB on older systems.
