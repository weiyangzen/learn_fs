# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/io.c

Implements virtual filesystem I/O for the FAT checker, including delayed write tracking and ReactOS NT-handle based disk access.

Key elements:
- `CHANGE` records queued writes: data buffer, byte offset, size, and next pointer.
- ReactOS path wraps `NtReadFile`, `NtWriteFile`, `NtClose`, and a local `WIN32lseek` using `CurrentOffset`.
- `fs_open` opens the target volume and locks it when opened read-write.
- `fs_isdirty`, `fs_lock`, and `fs_dismount` call filesystem control codes for dirty check, lock/unlock, and dismount.
- `fs_read` reads from disk, then overlays any queued pending writes that overlap the requested range.
- `fs_test` probes readability.
- `fs_write` either writes immediately or queues a `CHANGE`.
- `fs_close` optionally flushes queued changes and returns whether anything changed.

Dependencies:
- Includes `vfatlib.h`, which pulls in ReactOS NDK APIs and checker headers.
- Uses `FsCheckFlags` through `rosglue.h` macros for immediate-write/read-write behavior.

Research notes:
- ReactOS volume I/O is sector-aligned to 512 bytes for reads/writes, preserving unaligned caller semantics by read-modify-write.
- Potential edge case: ReactOS `fs_read` and `fs_test` align based on `size`, not `seek_delta + size`; unaligned positions with aligned sizes can require more bytes than allocated/read.
- Delayed writes let checker logic reason over a patched filesystem image before deciding whether to commit.
