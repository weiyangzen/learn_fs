# File Research: sources/virtualization/libguestfs/daemon/stat.c

Nanosecond stat/lstat wrappers and batched lstat.

Important behavior:
- `stat_to_statns` maps `struct stat` into `guestfs_int_statns`, including optional block size, block count, and nanosecond fields.
- `do_statns` follows symlinks; `do_lstatns` does not.
- `do_internal_lstatnslist` opens a directory fd and runs `fstatat(..., AT_SYMLINK_NOFOLLOW)` for each name.
- Per-entry failures in the batched API are represented by `st_ino = -1`, not total failure.
- Directory fd close failure is reported as a total error.

Filesystem relevance: high-resolution guest file metadata retrieval.
