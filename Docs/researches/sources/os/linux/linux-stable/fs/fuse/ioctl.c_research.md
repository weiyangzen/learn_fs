# File Research: sources/os/linux/linux-stable/fs/fuse/ioctl.c

## Purpose
Implements FUSE ioctl handling, including CUSE/FUSE compatibility details, unrestricted ioctl retry/deep-copy behavior, fs-verity ioctl sizing, compat ioctl dispatch, and private ioctl helpers used for file attribute get/set.

## Key Interfaces
- `fuse_do_ioctl()` is the core ioctl request loop.
- `fuse_ioctl_common()`, `fuse_file_ioctl()`, and `fuse_file_compat_ioctl()` are VFS-facing dispatch wrappers.
- `fuse_fileattr_get()` and `fuse_fileattr_set()` tunnel Linux file attribute ioctls through FUSE.
- `fuse_priv_ioctl()` sends kernel-originated ioctl requests on a temporary FUSE file handle.

## Control Flow And Behavior
Restricted ioctls derive in/out iovecs from `_IOC_*` command encoding; unrestricted ioctls allow the server to return `FUSE_IOCTL_RETRY` with requested input/output iovecs. The kernel copies user memory into folios, sends `FUSE_IOCTL`, copies server output back to user iovecs, and validates retry iovecs for count, size, overflow, and compat pointer representation.

Older protocol minors use ABI-sensitive iovec decoding for 32-bit CUSE servers. `FS_IOC_MEASURE_VERITY` and `FS_IOC_ENABLE_VERITY` receive special setup so digest, salt, and signature buffer sizes are known.

## Dependencies
Uses FUSE request helpers, folio/page transfer helpers, iov iterators, compat ABI helpers, file attribute APIs, fs-verity structures, and private FUSE open/release helpers.

## Risks And Invariants
Server-provided retry vectors are untrusted and must stay within `fc->max_pages`. Restricted mode must reject retries. `-ENOSYS` is translated to `-ENOTTY` for ioctl semantics. Partial output larger than the declared output size is treated as protocol error.
