<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h -->
# sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h

Source path: `sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h`

## Purpose
Declares the FUSE3 callback-handler functions implemented by the sample extension.

## Important APIs, Types, And Functions
Functions/prototypes: `ext_destroy`, `ext_statfs`, `ext_getattr`, `ext_opendir`, `ext_releasedir`, `ext_readdir`, `ext_mkdir`, `ext_rmdir`, `ext_open`, `ext_create`, `ext_read`, `ext_write`, `ext_flush`, `ext_truncate`, `ext_release`, `ext_unlink`, `ext_rename`, `ext_symlink`, plus 4 more. Includes: `stddef.h`, `stdio.h`, `fuse3/fuse.h`. Defines: `__CALLBACK_HANDLERS_H__`, `FUSE_USE_VERSION`.

## Control Flow
The exported `ext_*` prototypes mirror the supported FUSE operation subset: lifecycle, stat/getattr, directory operations, file open/create/read/write/flush/truncate/release, unlink/rename, symlink/readlink, fsync/fsyncdir, and chmod. `extension3.c` imports this header to populate the operation table.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stddef.h`, `stdio.h`, `fuse3/fuse.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
Prototype compatibility is tied to FUSE3 signatures, especially `readdir`, `rename`, and `truncate`. Any mismatch with the libfuse headers used by blobfuse2 would fail at build time or produce unsafe callback dispatch.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/libs/test_extension3/callback_handler.h -->
