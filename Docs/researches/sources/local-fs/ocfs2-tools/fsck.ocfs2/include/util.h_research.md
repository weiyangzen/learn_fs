# File Research: sources/local-fs/ocfs2-tools/fsck.ocfs2/include/util.h

Read coverage: complete file read, 97 lines.

Purpose: declares common fsck utilities, exit codes, cache controls, bitmap wrappers, write helpers, slot-system-file iteration, abort handling, and resource tracking.

Key details:
- Defines e2fsck-compatible exit-code bitmask constants.
- Defines cache modes: none, journal-sized, and full recovery cache.
- Declares inode writeback, cluster allocation marking, publish-block reading, bit counting, slot-system-file handling, and resource statistics.
- Bitmap set/clear macros pass caller function names into fatal-on-error wrappers.

Dependencies: `fsck.h`, libocfs2 bitmap/I/O/stat APIs.

Risk notes:
- Bitmap wrapper comments state bitmap operations are not expected to fail and should abort if they do.
- Exit-code constants are part of the command-line compatibility contract.
