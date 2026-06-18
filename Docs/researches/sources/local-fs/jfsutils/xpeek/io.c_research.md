# File Research: sources/local-fs/jfsutils/xpeek/io.c

Provides unaligned byte-range read/write wrappers over libfs block I/O.

APIs:
- `xRead(int64_t address, unsigned count, char *buffer)`.
- `xWrite(int64_t address, unsigned count, char *buffer)`.

Behavior:
- Computes `offset = address & (bsize - 1)`.
- Rounds the affected range up to whole aggregate blocks.
- If the request is already block-aligned and block-sized, directly calls `ujfs_rw_diskblocks`.
- Otherwise reads the containing block-aligned range into a temporary buffer.
- `xRead` copies the requested subrange out.
- `xWrite` copies the caller buffer into the temporary block buffer and writes the whole aligned range back.

Integration points:
- Used throughout `xpeek` for structure reads/writes at byte offsets that may not be block aligned.
- Depends on globals `fp` and `bsize`, plus `devices.h`.

Notable behavior and risks:
- Uses bitwise `&` instead of logical `&&` in `if ((offset == 0) & (length == count))`; works for 0/1 comparison results but is non-idiomatic.
- No overflow checks for `offset + count + bsize - 1`.
- Read-modify-write behavior in `xWrite` can overwrite adjacent bytes if the underlying read buffer is stale due to concurrent device changes.
