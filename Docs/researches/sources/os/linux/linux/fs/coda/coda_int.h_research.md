# File Research: sources/os/linux/linux/fs/coda/coda_int.h

Internal Coda declarations shared across module files.

Declares:
- Filesystem type: `coda_fs_type`.
- Tunables/globals: `coda_timeout`, `coda_hard`, `coda_fake_statfs`.
- Inode cache lifecycle: `coda_init_inodecache()`, `coda_destroy_inodecache()`.
- Shared fsync: `coda_fsync()`.

Sysctl integration:
- When `CONFIG_SYSCTL` is enabled, declares `coda_sysctl_init()` and `coda_sysctl_clean()`.
- Otherwise provides empty inline stubs.

Role:
- Keeps module-global declarations out of broader public Coda headers.
