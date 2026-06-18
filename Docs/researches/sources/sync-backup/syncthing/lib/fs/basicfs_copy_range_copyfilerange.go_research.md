## sources/sync-backup/syncthing/lib/fs/basicfs_copy_range_copyfilerange.go

Purpose: Linux copy-range backend using `copy_file_range`.

Important APIs/types/functions: `init` registers `CopyRangeMethodCopyFileRange`; `copyRangeCopyFileRange` loops until requested bytes are copied.

Control flow: For each loop, calls `unix.CopyFileRange` with explicit source/destination offsets so file offsets are not changed. Zero bytes with nil error is treated as unexpected EOF. `EAGAIN` is retryable; positive byte counts reduce remaining size.

State and persistence: Mutates destination file content and advances local offset variables only.

Dependencies and integration points: Linux build tag; uses `withFileDescriptors` adapter and copy-range method registry.

Risks: Kernel/filesystem support varies; errors should trigger fallback by higher-level copy-range selection. Large sizes are cast to `int` per syscall call.

Test signals: No direct tests here; copy-range integration tests should cover fallback behavior.
