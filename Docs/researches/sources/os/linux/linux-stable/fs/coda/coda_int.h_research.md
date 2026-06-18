# File Research: sources/os/linux/linux-stable/fs/coda/coda_int.h

## Purpose
Declares internal Coda module globals and lifecycle helpers shared across implementation files.

## Main Contents
- External module/global declarations: `coda_fs_type`, `coda_timeout`, `coda_hard`, `coda_fake_statfs`.
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`.
- `coda_fsync()` prototype.
- Sysctl lifecycle wrappers: real prototypes under `CONFIG_SYSCTL`, no-op inlines otherwise.

## Integration Points
Used by Coda module initialization, sysctl support, and file/dir operation code.

## Risks And Review Focus
- Header is intentionally small; global behavior changes should remain coordinated with module init and sysctl code.
