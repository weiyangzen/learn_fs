# File Research: sources/os/bsd/netbsd-src/lib/librt/shm.c

Read completely: 141 lines.

Implements POSIX shared-memory object naming over a tmpfs directory. `_shm_check_fs()` verifies `/var/shm` exists, is mounted as tmpfs, and has sticky world-writable directory permissions before caching success in `shm_ok`.

`_shm_get_path()` enforces POSIX-style names beginning with `/` and rejects additional slashes, then maps the name to `/var/shm/.shmobj_<name>`. `shm_open()` opens that path with `O_CLOEXEC | O_NOFOLLOW`, and `shm_unlink()` unlinks it.

If the backing directory is absent or invalid, operations fail with `ENOTSUP`; bad names fail with `EINVAL`; overly long mapped paths fail with `ENAMETOOLONG`.
