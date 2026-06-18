<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c`

## Purpose
Implements the sample FUSE3 extension callback layer. Each `ext_*` function logs the operation and forwards it to the `storage_callbacks` table supplied by blobfuse/blobfuse2, with one explicit filter that hides `/subtree.sh` by returning `-ENOENT` from `ext_getattr`.

## Important APIs, Types, And Functions
Functions/prototypes: `ext_init`, `ext_destroy`, `ext_statfs`, `ext_getattr`, `ext_opendir`, `ext_releasedir`, `ext_readdir`, `ext_mkdir`, `ext_rmdir`, `ext_open`, `ext_create`, `ext_read`, `ext_write`, `ext_flush`, `ext_truncate`, `ext_release`, `ext_unlink`, `ext_rename`, plus 5 more. Includes: `stdio.h`, `stdlib.h`, `syslog.h`, `errno.h`, `string.h`, `extension3.h`. Defines: none declared.

## Control Flow
Runtime flow is extension entrypoint to callback handler to stored backend operation: `extension3.c` registers these functions into a `struct fuse_operations`, blobfuse calls them through libfuse, and the handlers delegate to the original storage callbacks. `ext_init` and `ext_destroy` include extra presence checks, while most file, directory, symlink, sync, and chmod handlers assume the corresponding backend callback is populated.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `syslog.h`, `errno.h`, `string.h`, `extension3.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
Several delegated callbacks are called without null checks; an incomplete storage callback table can crash the process. The `/subtree.sh` filter is hard-coded and should be treated as test behavior rather than a general policy engine. Because all state is a global callback table, concurrent extension instances would share backend pointers.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.c -->
