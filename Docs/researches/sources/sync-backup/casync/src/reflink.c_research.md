# sources/sync-backup/casync/src/reflink.c

Purpose: attempts copy-on-write reflinks between regions of two file descriptors, with block-aligned fallbacks and optional validation.

Important APIs/types/functions: `reflink_fd` is the public entry. Helpers include `pread_try_harder`, which reopens `/proc/self/fd/N` to pread from fds that may not support pread, and `validate`, which byte-compares copied ranges when enabled.

Control flow/state: the function aligns offsets to 4096-byte filesystem blocks, uses `FICLONERANGE`, tracks bytes reflinked in `ret_reflinked`, and returns negative errno on unsupported or invalid requests. It avoids partial unaligned regions that the kernel cannot clone.

Dependencies/integration: Linux `ioctl(FICLONERANGE)`, `struct file_clone_range`, fd utilities, and extraction/seed code that can optimize matching extents.

Risks/test signals: assumes 4096-byte block size, so filesystems with different clone granularity may underperform or fail. Validation is compile-time and expensive. Tests around seeded extraction and sparse/hardlink behavior provide indirect signals.

Source research group: `subset-b-009122`.
