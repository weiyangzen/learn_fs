# sources/user-network-fs/libfuse/util/fuser_conf.c

## Purpose
Parses `fuse.conf`, counts current FUSE mounts, manages privilege dropping/restoration for setuid helpers, and enforces non-root mount policies.

## Important APIs, Types, And Functions
- Globals `user_allow_other` and `mount_max`.
- `read_conf` parses `FUSE_CONF`.
- `count_fuse_fs` uses Linux `listmount/statmount` when available, otherwise mtab.
- `drop_privs` and `restore_privs` switch fsuid/fsgid to real uid/gid and back.
- `check_nonroot_mount_count`, `check_nonroot_dir_access`, and `check_nonroot_fstype` enforce policy.
- `unescape` and the `GETMNTENT` wrapper support libc variants that do not unescape mtab fields.

## Control Flow
Configuration parsing strips comments/trailing whitespace, parses known lines, and reports unknown parameters. Mount counting reads kernel mount info or mtab and counts `fuse`/`fuse.*`. Non-root checks enforce mount-count limits, sticky directory ownership, write access, and an underlying filesystem whitelist.

## State And Persistence
Global process state reflects parsed config. `drop_privs` stores prior fsuid/fsgid in static variables and must be balanced with `restore_privs`. No persistent writes occur.

## Dependencies And Integration Points
Used by `fusermount.c`, `mount_service.c`, and `mount.fuse.c` build targets. Depends on `FUSE_CONF`, mtab APIs, Linux listmount/statmount feature detection, and `mount_flags` declarations.

## Risks
Privilege state is static and not nest-safe. The filesystem whitelist is security critical and must be updated carefully. If `listmount` pagination or `req.param` semantics differ across kernels, count fallback behavior should be verified. Fatal/nonfatal config open errors affect setuid helper behavior.

## Test Signals
Run parser tests for comments, whitespace, long lines, unknown keys, negative mount_max, and missing files. Test mount counting through listmount and mtab, sticky-bit ownership, access failures, and each whitelisted/non-whitelisted filesystem type.
