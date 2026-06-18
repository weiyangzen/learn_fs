# sources/user-network-fs/pyfuse3/examples/tmpfs.py

Purpose: Implements a complete in-memory example filesystem for pyfuse3, backed by an in-memory SQLite database. It demonstrates async FUSE operation handlers, inode metadata management, directory contents, file IO, symlinks, links, renames, truncation, statfs, and mount lifecycle.

Important APIs/types/functions: `Operations(pyfuse3.Operations)` is the main filesystem implementation. `init_tables` creates `inodes` and `contents` tables and the root inode. `get_row` enforces one-row SQL lookups. FUSE handlers include `lookup`, `getattr`, `readlink`, `opendir`, `readdir`, `unlink`, `rmdir`, `symlink`, `rename`, `link`, `setattr`, `mknod`, `mkdir`, `statfs`, `open`, `access`, `create`, `read`, `write`, and `release`. `NoUniqueValueError` and `NoSuchRowError` model internal SQL lookup failures. `parse_args` and the `__main__` block initialize logging, options, `pyfuse3.init`, `trio.run(pyfuse3.main)`, and `pyfuse3.close`.

Control flow: FUSE lookups read directory entries from `contents` and then call `getattr` to return `EntryAttributes`. Creation inserts a new inode and a directory entry, returning attributes. Removal deletes the directory entry and deletes the inode only when the link count is one and the inode is not open. Rename either updates a directory row or delegates replacement to `_replace`. Reads and writes use the file handle as the inode id and update/read the `data` blob. `release` decrements open counts and performs deferred inode deletion for unlinked but still-open files.

State and persistence: All data lives in `sqlite3.connect(':memory:')`, so it is process-local and non-persistent. Metadata is split between `inodes` rows and `contents` directory rows. `inode_open_count` tracks open handles for deferred deletion. The code does not maintain kernel lookup counts, generation numbers, or normal atime/mtime/ctime updates beyond explicit `setattr` and create-time initialization.

Dependencies and integration points: Depends on `trio`, `pyfuse3`, `sqlite3`, POSIX `errno/stat/os`, and pyfuse3 C extension types. It integrates with pyfuse3 through subclassed async operation handlers and uses `pyfuse3.readdir_reply`, `FileInfo`, `EntryAttributes`, and `StatvfsData`.

Risks: This is deliberately simple and unsuitable for significant data. Directory emptiness checks count all children, including the root's `..` row pattern; link count behavior is approximate. Write slicing does not fill sparse holes if `off` is beyond current data. SQLite writes are not explicitly committed, relying on connection behavior. It discards nonzero rename flags and does not implement permissions in `access`.

Test signals: `test/test_examples.py::test_tmpfs` mounts this example and exercises writes, mkdir, symlink, mknod, chown, chmod, utimens, rounding, links, rename, readdir, statvfs, truncation, and unlink while-open behavior.
