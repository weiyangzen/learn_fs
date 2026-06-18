# File Research: sources/os/linux/linux/fs/exportfs/expfs.c

Read status: complete, 610 lines.

This file implements generic VFS export helpers used by NFS export and file-handle users. It maps inodes/dentries to file handles and decodes file handles back to dentries, including reconnecting disconnected dentries to the dcache tree when subtree checks require a connected path.

Key responsibilities:
- Default `get_name()` implementation: scans a parent directory with `iterate_dir()` to find the entry matching a child inode number.
- File-handle encoding via `exportfs_encode_inode_fh()` and `exportfs_encode_fh()`, delegating to filesystem `export_operations` when present.
- Fallback non-decodeable 64-bit inode/generation file IDs for fanotify-style use when full export decode support is unavailable.
- File-handle decoding through `exportfs_decode_fh_raw()` and `exportfs_decode_fh()`.
- Dentry reconnect logic for disconnected dentries: `reconnect_path()`, `reconnect_one()`, `dentry_connected()`, and `clear_disconnected()`.
- Alias selection through `find_acceptable_alias()` to satisfy caller-provided export/subtree acceptance checks.

Important data/control flow:
- Encoding checks `exportfs_can_encode_fh()` and rejects unsupported user flag bits in returned file ID types.
- Decoding calls filesystem `fh_to_dentry`; for directories it may reconnect to root before applying `acceptable()`.
- For non-directories, decoding first tries acceptable aliases; if needed, it decodes the parent via `fh_to_parent`, reconnects that parent, finds the child name, looks it up, verifies inode identity, and then rechecks aliases.
- `exportfs_decode_fh()` normalizes most decode errors to `-ESTALE`, except `-ENOMEM`.

Concurrency and safety:
- Alias walking uses `inode->i_lock` and reference-safe dentry handling.
- Reconnect paths tolerate rename/unlink races by rechecking whether dentries became connected or stale.
- Directory scanning uses `vfs_getattr_nosec()` instead of directly trusting `i_ino`, which matters for 64-bit inode numbers on 32-bit hosts.
- Strictly rejects invalid fileid types with user flag bits set.

External dependencies:
- Uses filesystem-provided `struct export_operations`.
- Integrates with VFS dentries, mounts, path lookup, credentials, directory iteration, and NFS export documentation assumptions.

Research notes:
- This file is generic infrastructure, not tied to one filesystem.
- Correctness depends heavily on dcache aliasing and reconnect semantics.
- It is the bridge between stable file handles and volatile VFS dentries.
