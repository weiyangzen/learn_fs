# File Research: sources/local-fs/xfsdump/librmt/rmtfstat.c

Implements `rmtfstat(fildes, struct stat *buf)`.

Behavior:
- Local descriptors call `fstat(2)`.
- Remote descriptors send `Z<fd>\n`, read a byte count from `_rmt_status()`, then copy up to `sizeof(struct stat)` bytes into the caller buffer.
- Extra remote bytes are drained.

Notable assumption:
- The code comments acknowledge that direct binary copying of `struct stat` is non-portable and depends on compatible layout/padding.
