# sources/test-tools/strace/src/fchownat.c

Decoder for `fchownat`. It prints directory fd, pathname, uid, gid, and flags. State is only syscall arguments. Dependencies are path/dirfd printers, uid/gid formatting, and `AT_*` flag decoding from common helpers. Risks are null or inaccessible path handling, `AT_EMPTY_PATH`, `AT_SYMLINK_NOFOLLOW`, and uid/gid values that need namespace-aware rendering. Tests should cover normal paths, `AT_FDCWD`, empty paths, symlink flags, and invalid pointer failures.
