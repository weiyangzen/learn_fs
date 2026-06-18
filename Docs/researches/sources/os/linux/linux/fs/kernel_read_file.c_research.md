# File Research: sources/os/linux/linux/fs/kernel_read_file.c

Kernel helper implementation for reading regular-file contents into kernel memory with LSM mediation.

Key responsibilities:
- Implements `kernel_read_file()` for full or chunked reads into caller-provided or internally allocated buffers.
- Rejects invalid partial-read combinations, non-regular files, empty files, oversized files, and whole-file reads that cannot fit the provided buffer.
- Temporarily denies write access while reading.
- Calls `security_kernel_read_file()` before reading and `security_kernel_post_read_file()` after complete whole-file reads.
- Allocates with `vmalloc()` when the caller passes `*buf == NULL`, and frees on error.
- Exposes convenience wrappers for paths in the caller namespace, paths relative to init namespace root, and file descriptors.

Important interactions:
- Uses `kernel_read()`, `filp_open()`, `file_open_root()`, `get_fs_root()`, fd-class cleanup, and LSM hooks.
- Exported GPL symbols are used by kernel subsystems that load firmware, certificates, modules, policies, or other kernel-consumed file content.

Invariants and risks:
- `offset != 0` is allowed only for caller-managed partial reads with an existing buffer and `file_size` output.
- Whole-file reads require exact EOF position matching; short reads return `-EIO`.
- `deny_write_access()`/`allow_write_access()` must stay balanced on every exit path.
- File contents can change between chunked calls, so the interface documents chunked reads as discouraged.
