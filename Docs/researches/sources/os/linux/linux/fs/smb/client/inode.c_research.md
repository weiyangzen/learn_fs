# File Research: sources/os/linux/linux/fs/smb/client/inode.c

## Purpose
Implements CIFS/SMB inode construction, attribute conversion, metadata revalidation, create/delete/rename directory operations, setattr/truncate, getattr, fiemap, cache invalidation, and inode operation selection.

## Main Interfaces
- Inode setup and lookup: `cifs_fattr_to_inode()`, `cifs_fill_uniqueid()`, `cifs_iget()`, `cifs_root_iget()`.
- Metadata fetch: `cifs_get_inode_info()`, `smb311_posix_get_inode_info()`, `cifs_get_inode_info_unix()`.
- Attribute conversion: `cifs_unix_basic_to_fattr()`, `wire_mode_to_posix()`, SMB3 POSIX and non-POSIX open-info converters.
- Namespace mutations: `cifs_unlink()`, `cifs_mkdir()`, `cifs_rmdir()`, `cifs_rename2()`.
- Revalidation/stat: `cifs_revalidate_file_attr()`, `cifs_revalidate_dentry_attr()`, `cifs_revalidate_mapping()`, `cifs_getattr()`.
- Size/attribute mutation: `cifs_file_set_size()`, `cifs_set_file_info()`, `cifs_setattr()`.

## Control Flow
Attribute lookup chooses among SMB3 POSIX info, legacy Unix extensions, and regular SMB file-all-info. Reparse points are routed through `reparse_info_to_fattr()` so symlinks, name-surrogate junctions, and unsupported reparse points are either translated locally or left for server-side open handling. The resulting `cifs_fattr` is normalized for mount options such as server inode numbers, ACL-derived modes, SFU emulation, Minshall+French symlinks, readonly DOS attributes, and fake DFS junction attributes before updating or instantiating the inode.

Mutating operations build a full dentry path, acquire a tcon link, call dialect operations, then invalidate parent/child timestamps and dcache state as needed. Delete and rename paths handle busy/open files by closing deferred handles, doing SMB2+ silly-rename behavior, retrying after clearing readonly attributes, and marking open handles as delete-pending.

## State And Synchronization
The file updates CIFS inode fields under `inode->i_lock`, uses CIFS inode flags such as `CIFS_INO_INVALID_MAPPING`, `CIFS_INO_DELETE_PENDING`, and `CIFS_INO_TMPFILE`, and coordinates mapping invalidation with `wait_on_bit_lock_action()` on `CIFS_INO_LOCK`. Size updates are coordinated with netfs remote size, pagecache truncation, fscache resize/invalidation, and outstanding netfs IO waits.

## Integration Points
Uses dialect callbacks in `server->ops` for query path/file info, open, close, unlink, mkdir, rmdir, rename, set size, set info, ACL, symlink, fiemap, and reparse operations. It depends on `reparse.c`, `link.c`, `cached_dir.c`, ACL helpers, DFS mount handling, fscache/netfs, and VFS inode/dentry operation tables from `cifsfs.c`.

## Notable Behaviors
- Auto-disables server inode numbers when collisions or bad root inode numbers are detected.
- Treats DFS referrals and name-surrogate directory reparse points as automount junction directories.
- Avoids path-based size updates when a writable handle can be used.
- Suppresses explicit timestamp setting for `O_TRUNC`/`ftruncate` cases to preserve server automatic timestamp behavior.
- Forces revalidation for ACL-derived modes, SFU special files, MF symlinks, some reparse points, hardlinked `noserverino` files, and stale cached attributes.

## Risks And Review Focus
- Inode number collision handling is correctness-sensitive for hardlinks and dcache aliasing.
- Delete/rename fallback behavior touches deferred close, silly rename, readonly attributes, and dentry hashing.
- Reparse point classification must not misrepresent unsupported server-side objects.
- Setattr paths mix local permission checks, ACL updates, DOS attributes, truncation, fscache, and netfs state.
