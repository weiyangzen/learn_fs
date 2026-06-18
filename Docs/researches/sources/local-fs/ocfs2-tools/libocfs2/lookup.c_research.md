# File Research: sources/local-fs/ocfs2-tools/libocfs2/lookup.c

Implements name lookup inside a single OCFS2 directory.

Main API:
- `ocfs2_lookup(fs, dir, name, namelen, buf, inode)` returns the inode block number for `name` in directory `dir`.

Non-indexed path:
- Uses `ocfs2_dir_iterate()` and `lookup_proc()`.
- `lookup_proc()` compares `name_len & 0xFF` and name bytes, stores `dirent->inode`, marks found, and aborts iteration.

Indexed directory path:
- Reads the directory inode to check indexed-directory support.
- `ocfs2_find_entry_dx()` reads the dx root block from `di->i_dx_root`, hashes the name with `ocfs2_dx_dir_name_hash()`, searches via `ocfs2_dx_dir_search()`, and returns the found dx entry inode.
- Lookup result resources are released through `release_lookup_res()`.

Behavior:
- Returns `OCFS2_ET_FILE_NOT_FOUND` when no matching entry is found.
- Caller-provided `buf` can be passed to directory iteration as a block buffer; the function separately allocates its own inode buffer for checking directory features.

Debug utility:
- The `DEBUG_EXE` path can traverse a path component by component starting at root or a user-provided inode block.
