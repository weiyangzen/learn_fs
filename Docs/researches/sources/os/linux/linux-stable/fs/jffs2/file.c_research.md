# File Research: sources/os/linux/linux-stable/fs/jffs2/file.c

## Role

Implements regular-file operations and address-space operations for JFFS2, including folio read, write begin/end, and fsync.

## VFS Tables

- `jffs2_file_operations` uses generic llseek/open/read/write, readonly mmap preparation, splice helpers, ioctl, fsync, and file lease support.
- `jffs2_file_inode_operations` wires ACL, setattr, and xattr listing hooks.
- `jffs2_file_address_operations` provides `read_folio`, `write_begin`, and `write_end`.

## Read Path

- `jffs2_do_readpage_nolock()` maps the folio locally and fills it via `jffs2_read_inode_range()`.
- `__jffs2_read_folio()` performs the read and unlocks the folio.
- `jffs2_read_folio()` wraps the read with the inode-private `f->sem`.

## Write Begin

- If writing beyond EOF, writes a zero-compressed hole node covering old EOF to new position.
- Adds the hole dnode to the inode fragment tree and obsoletes metadata-only node if needed.
- Locks `c->alloc_sem` while acquiring and reading the target folio to avoid GC/read deadlocks.
- Ensures the folio is uptodate before write completion.

## Write End

- Writes the changed range as a new JFFS2 raw inode node via `jffs2_write_inode_range()`.
- Expands the write to the whole page when the write reaches page end, reducing fragmentation for short append-heavy workloads.
- Updates inode size, block count, mtime, and ctime on extension.
- Marks the folio not uptodate if fewer bytes reached flash than were copied into cache.

## Fsync

`jffs2_fsync()` waits for dirty page-cache data, locks the inode, and triggers write-buffer GC flushing for the inode number.

## Research Notes

JFFS2 files are represented as a fragment tree of log nodes rather than block mappings. The file write path appends new inode nodes and updates in-memory fragments, while read reconstructs data ranges through `read_inode_range()`.
