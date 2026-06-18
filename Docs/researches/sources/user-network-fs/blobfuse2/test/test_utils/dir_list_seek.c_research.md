<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c -->
# sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c

Source path: `sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c`

## Purpose
Exercises low-level directory listing and seek behavior, including direct syscall-level directory reads.

## Important APIs, Types, And Functions
Functions/prototypes: `main`. Includes: `dirent.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `sys/stat.h`, `sys/syscall.h`. Defines: `handle_error`, `BUF_SIZE`.

## Control Flow
The program opens a directory, reads entries into a fixed buffer, and inspects listing offsets to catch directory cursor behavior that higher-level APIs may hide.

## State And Persistence
State is process-local C state plus filesystem effects through FUSE/POSIX operations. Extension files rely on the global `storage_callbacks` table and, for FUSE3 registration, `signature_verified`; utility programs persist only the files or directory entries they create through the mounted filesystem.

## Dependencies And Integration Points
Depends on `dirent.h`, `fcntl.h`, `stdio.h`, `unistd.h`, `stdlib.h`, `sys/stat.h`, `sys/syscall.h` and integrates with blobfuse2's extension loader, libfuse callback dispatch, or shell-driven test harnesses under `test/scripts`.

## Risks
It depends on Linux directory syscall semantics and fixed buffer sizing, so portability is low and failures may be kernel/libc-specific.

## Test Signals
Useful signals are successful compilation against the target FUSE headers, expected exit status from helper programs, syslog/debug output for extension callbacks, and observable mount-side behavior such as hidden paths, flushed writes, or directory offset handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/test/test_utils/dir_list_seek.c -->
