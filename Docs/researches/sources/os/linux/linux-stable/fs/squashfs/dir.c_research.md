# File Research: sources/os/linux/linux-stable/fs/squashfs/dir.c

## Summary
Implements `readdir` for Squashfs directories over packed, compressed directory metadata.

## Key APIs
- `squashfs_dir_ops`.

## Important Behavior
Squashfs does not store `.` and `..` directory entries, so `squashfs_readdir()` synthesizes them and offsets external `ctx->pos` by 3 relative to on-disk directory positions.

For indexed long directories, `get_dir_index_using_offset()` scans directory index entries to find the metadata block nearest the requested `f_pos`. Index failures are tolerated because the index is an optimization.

The main loop reads directory headers and entries, validates counts, name lengths, and directory entry types, computes inode numbers from the header base plus entry delta, and emits VFS dirents.

## Risks
Malformed directory metadata is handled as a read failure and stops iteration. Correct `ctx->pos` translation is important because seeking in directories depends on stable external offsets that include synthetic entries.
