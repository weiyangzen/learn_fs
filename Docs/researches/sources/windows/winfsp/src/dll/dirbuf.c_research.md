# File Research: sources/windows/winfsp/src/dll/dirbuf.c

Sorted directory enumeration buffer used by user-mode filesystems to cache and replay directory entries.

Key responsibilities:
- Defines an internal `FSP_FILE_SYSTEM_DIRECTORY_BUFFER` with an SRW lock, capacity marks, and a single byte buffer.
- Stores directory records from the low end of the buffer and an index array from the high end.
- Grows allocation from a low bound of 256 bytes up to a high bound of 1 MiB using different growth factors.
- Orders `"."` and `".."` before normal names.
- Sorts entries by filename using an internal non-recursive quicksort.
- Supports binary search by marker for resume-style directory reads.
- Exposes acquire, fill, release/sort, read, delete, and peek functions.

Important behavior:
- `FspFileSystemAcquireDirectoryBufferEx` lazily creates the buffer under a static create lock and returns it already exclusively locked when reset/created.
- `FspFileSystemFillDirectoryBuffer` appends an `FSP_FSCTL_DIR_INFO` and records its offset in the index.
- `FspFileSystemReleaseDirectoryBuffer` removes invalidated index entries and sorts the remaining index.
- `FspFileSystemReadDirectoryBuffer` acquires shared access, seeks past an optional marker, copies entries to the caller buffer, then appends the terminating zero-sized entry.
- `FspFileSystemDeleteDirectoryBuffer` frees the data buffer and header.

Dependencies:
- Includes `dll/library.h`.
- Uses `FspFileSystemAddDirInfo`, `invariant_wcsncmp`, `MemAlloc`, `MemRealloc`, `MemFree`, interlocked pointer helpers, SRW locks, and WinFsp `FSP_FSCTL_DIR_INFO`.

Notable risks:
- The caller contract requires acquire/fill/release discipline; fill and peek assume the exclusive lock is already held.
- Sorting relies on an index count derived from capacity/high mark, so buffer mark integrity is critical.
