# File Research: sources/local-fs/erofs-utils/lib/io.c

This file implements the generic `erofs_vfile` I/O abstraction plus native fd/device/blob helpers. It supports real file descriptors, dry-run mode, and overrideable virtual file operations.

Main groups:
- Write/read helpers: `__erofs_io_write`, `erofs_io_pwrite`, `erofs_io_pwritev`, `erofs_io_pread`, `erofs_io_read`, `erofs_io_write`.
- File maintenance: `erofs_io_fstat`, `erofs_io_fsync`, `erofs_io_fallocate`, `erofs_io_ftruncate`, `erofs_io_lseek`, `erofs_io_close`.
- Device/blob management: `erofs_dev_open`, `erofs_dev_close`, `erofs_blob_open_ro`, `erofs_blob_closeall`, `erofs_dev_read`.
- Copy helpers: `erofs_copy_file_range`, `erofs_io_sendfile`, `erofs_io_xcopy`.

Important behavior:
- If `cfg.c_dry_run` is set, write/truncate/fallocate/fsync operations become no-ops and fstat returns a synthetic regular-file mode.
- Every public `erofs_vfile` helper first delegates to `vf->ops` when present.
- `erofs_dev_open()` handles regular files and block devices. With truncation on regular files, it may unlink and recreate files on ext4/btrfs to avoid undesirable writeback after `truncate(0)`.
- Block devices are sized with `BLKGETSIZE64` / `BLKGETSIZE`, rounded to EROFS block size, and optionally discarded.
- `erofs_dev_read()` treats short reads as EOF and pads the destination with zeroes.
- Copy paths prefer kernel helpers (`copy_file_range`, `sendfile`, `pwritev`) and fall back to buffered loops.

Notable dependencies:
- `erofs_vfile` ops from `erofs/internal.h`.
- Linux block ioctls and fallocate/discard when available.
- Global config `cfg`.

Risks / notes:
- The native `erofs_io_pwrite()` and `erofs_io_pread()` loops advance `buf` and `pos`, but the syscall length argument remains `len` rather than remaining length. If a short read/write occurs, this should be audited because callers expect exact accounting.
- `erofs_io_xcopy()` decrements requested length by bytes read even if a later pwrite writes fewer bytes than read; it treats negative writes but not partial writes as fatal.
- The abstraction is performance-sensitive because it sits beneath metadata flush, image writes, remote-backed vfiles, and diskbuf copies.
