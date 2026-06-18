<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/readwrite.c -->
# sources/user-network-fs/blobfuse2/test/scripts/readwrite.c

Source path: `sources/user-network-fs/blobfuse2/test/scripts/readwrite.c`

## Purpose
Small C utility for repeated read/write timing through mounted storage.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `stdio.h`, `stdlib.h`, `time.h`, `unistd.h`. Defines: none declared.

## Control Flow
The utility loops over simple POSIX file operations and uses wall-clock timing to produce a throughput-oriented signal for scripts.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `stdio.h`, `stdlib.h`, `time.h`, `unistd.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
The helper is benchmark scaffolding rather than a correctness oracle; OS cache effects and missing fsync semantics can skew results.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/scripts/readwrite.c -->
