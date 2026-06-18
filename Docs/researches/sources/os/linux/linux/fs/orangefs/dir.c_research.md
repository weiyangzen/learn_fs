# File Research: sources/os/linux/linux/fs/orangefs/dir.c

Implements OrangeFS directory file operations and readdir buffering.

Key behavior:
- `orangefs_dir` tracks the server readdir token, linked list of received directory parts, logical end position, and sticky error state.
- `do_readdir()` sends `ORANGEFS_VFS_OP_READDIR`, obtains a readdir slot, handles daemon restart/purge retries, validates trailer size, and updates the continuation token.
- Readdir trailers begin with `orangefs_readdir_response_s`; following entries are encoded as string length, string, padding, khandle, and padding.
- `parse_readdir()` stores trailer buffers as linked `orangefs_dir_part` nodes.
- `fill_from_part()` decodes entries from the current `ctx->pos`, emits names with inode numbers derived from khandles, and treats corrupt/invalid positioning as `EIO`.
- `orangefs_dir_iterate()` synthesizes `.` and `..`, reads more parts as needed, fills userspace buffers, and enforces position validity.
- `orangefs_dir_llseek()` frees cached parts and resets token when seeking backward.

Important details:
- Directory positions encode part number and byte offset using `PART_SHIFT`.
- Directory data is vmalloc-backed trailer memory freed on release or seek reset.
