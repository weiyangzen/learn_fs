# sources/user-network-fs/samba/source3/modules/vfs_crossrename.c

## Purpose
`vfs_crossrename.c` adds a fallback for `renameat()` failures with `EXDEV`, copying small regular files across filesystem boundaries and then unlinking the source.

## Important APIs, Types, And Functions
`crossrename_connect()` reads `crossrename:sizelimit` in MiB into a module-global byte limit. `copy_reg()` validates the source, enforces the size limit, unlinks the destination, opens both sides with `openat()`, copies data with `transfer_file()`, restores ownership/mode/timestamps, closes descriptors, and unlinks the source. `crossrename_renameat()` delegates first and only falls back on `EXDEV`.

## Control Flow
Normal rename is pass-through. Named streams are rejected with `ENOENT`. On `EXDEV`, `copy_reg()` performs copy-then-unlink and maps NTSTATUS back to errno.

## State And Persistence
The size limit is process-global. Filesystem data persists through direct POSIX writes; there is no rollback or transaction state.

## Dependencies And Integration Points
The module uses Samba pathref fds, next VFS rename/unlink, profiling, `transfer_file()`, and POSIX metadata syscalls. The copy path bypasses most lower VFS file-copy hooks.

## Risks
The fallback is not atomic, may remove an existing destination before copy success, and can leave partial files. Rename flags such as no-replace are not honored in the fallback. ACLs, xattrs, streams, and Samba metadata are not copied. Share-specific size limits can conflict because the variable is global.

## Test Signals
Simulate `EXDEV`, size-limit rejection, non-regular files, stream rejection, metadata restoration, destination existence, copy failure cleanup, and close/unlink failure mapping.
