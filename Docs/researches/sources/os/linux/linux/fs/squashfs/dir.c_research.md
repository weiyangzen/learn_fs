# File Research: sources/os/linux/linux/fs/squashfs/dir.c

Implements directory iteration for SquashFS.

Because `.` and `..` are not stored on disk, `squashfs_readdir()` synthesizes them and offsets external `ctx->pos` by 3. It can use long-directory indexes to jump near a requested position, then reads directory headers and entries from packed metadata.

It validates directory counts, name lengths, and directory entry types before emitting entries through `dir_emit()`.

Exports `squashfs_dir_ops` with generic read/llseek, shared iteration, and lease handling.
