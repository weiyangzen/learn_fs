<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c -->
# sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c

Source path: `sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c`

## Purpose
Tiny command-line helper that opens a file, writes data, and calls `fsync` to exercise explicit flush behavior through a mount.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `stdio.h`, `stdlib.h`, `fcntl.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `unistd.h`. Defines: none declared.

## Control Flow
The program validates arguments, opens the target with POSIX file APIs, writes the provided buffer, calls `fsync`, and exits with non-zero status on failure.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `fcntl.h`, `sys/types.h`, `sys/stat.h`, `string.h`, `unistd.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
It is intentionally minimal: no retry logic, limited diagnostics, and no verification that data reached remote storage beyond the local `fsync` return code.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/fsync_sample.c -->
