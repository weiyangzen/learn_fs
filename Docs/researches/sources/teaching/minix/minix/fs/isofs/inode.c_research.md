# File Research: sources/teaching/minix/minix/fs/isofs/inode.c

This file implements isofs inode cache management, directory loading, ISO9660 directory record parsing, and Rock Ridge integration.

Key entry points:
- `fs_putnode()`: decrements reference count for an opened inode.
- `get_inode(ino_nr)`: returns an active cached inode without incrementing.
- `open_inode(ino_nr)`: returns cached inode and increments `i_count`.
- `put_inode()`, `dup_inode()`: reference management.
- `read_directory(dir)`: reads and caches all entries of a directory.
- `read_inode(dir_entry, extent, offset)`: reads one ISO directory record, creates/reuses inode cache entry, parses ISO and Rock Ridge data.
- `inode_cache_get()` / `inode_cache_add()`: uthash-backed inode lookup/insert.

Parsing behavior:
- Directory inode numbers use extent location; file inode numbers use absolute directory record byte position.
- `read_inode_iso9660()` parses names, strips version suffixes, computes extents, timestamps, modes, sizes, block counts, and basic ownership.
- `read_inode_susp()` parses System Use/Rock Ridge data and overlays POSIX metadata, symlink target, alternate name, and reparented inode handling.

Directory cache:
- Uses a stack buffer for up to 256 entries, then allocates an exact-sized persistent array.
- Performs a second pass for directories larger than the stack buffer.
- Skips entries marked by Rock Ridge reparenting.

Notable risks:
- Memory allocation is permanent for cached directories/inodes; comments acknowledge structural improvement needed.
- `check_inodes()` is a stub that always returns true.
- Rock Ridge copied names allocate `name_length + 1` but copy only `name_length`, leaving terminator dependent on allocator zeroing.
