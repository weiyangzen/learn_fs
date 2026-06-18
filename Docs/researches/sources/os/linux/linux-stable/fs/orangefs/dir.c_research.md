# File Research: sources/os/linux/linux-stable/fs/orangefs/dir.c

## Scope

This file implements OrangeFS directory file operations and client readdir response parsing.

## APIs Covered

- Readdir transport: `do_readdir()`, `orangefs_dir_more()`.
- Trailer parsing and buffering: `parse_readdir()`, `fill_from_part()`, `orangefs_dir_fill()`.
- File operations: `orangefs_dir_llseek()`, `orangefs_dir_iterate()`, `orangefs_dir_open()`, `orangefs_dir_release()`, and `orangefs_dir_operations`.

## Control Flow And Behavior

- Directory stream state is stored per open file in `struct orangefs_dir`, with server token, linked response parts, end position, and sticky error.
- Part zero is synthesized for `.` and `..`; server data begins at part one.
- `ctx->pos` encodes part number in high bits and byte offset within a part in low bits.
- `do_readdir()` acquires a readdir slot, posts a READDIR op, retries if purged with `-EAGAIN`, and stores the returned continuation token.
- Server trailers start with `struct orangefs_readdir_response_s`; entry records contain name length, name, zero byte, padding, and object handle.
- Seek to an earlier offset with `SEEK_SET` discards cached parts so subsequent iteration can observe fresh directory state.

## Risks And Invariants

- Corrupt trailer layout or invalid userspace offsets are reported as `-EIO`.
- Trailer size must fit within `PART_SIZE`.
- Readdir slot accounting must balance `orangefs_readdir_index_get()` and `_put()`.
- Cached directory parts are `vfree()`d on release or reset.
