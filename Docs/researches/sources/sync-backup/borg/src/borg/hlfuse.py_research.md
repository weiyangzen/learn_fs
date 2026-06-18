# sources/sync-backup/borg/src/borg/hlfuse.py

## Purpose
Implements an alternate high-level FUSE backend using `mfusepy`. It exposes Borg archives as a read-only path-based filesystem with lazy archive expansion, versions mode, hard-link handling, xattrs, symlinks, and chunk-backed reads.

## Important APIs, Types, And Functions
`DirEntry` stores inode, parent, and lazily allocated children. `FuseBackend` manages tree construction and item packing with `_create_node`, `get_inode`, `set_inode`, `_create_filesystem`, `check_pending_archive`, `_iter_archive_items`, `_process_archive`, `_process_leaf_versioned`, `_file_version`, `_make_versioned_name`, `_find_node_from_root`, `_find_node`, handle helpers, and `_make_stat_dict`. `borgfs` implements `mount`, `statfs`, `getattr`, `listxattr`, `getxattr`, `open`, `release`, `create`, `read`, `readdir`, and `readlink`.

## Control Flow
Mount option parsing mirrors `fuse.py`. The filesystem tree uses path lookups instead of low-level inode callbacks. Archive directories are placeholders until accessed; `_find_node` expands pending archives along traversal. Items are msgpacked per inode to reduce Python object memory. Reads use file handles, last-position optimization, data chunk LRU cache, repository object parsing, and optional zero-fill for missing chunks.

## State And Persistence
State is in-memory: `DirEntry` tree, packed `inodes`, pending archive map, handles, LRU caches, version index, and mount option flags. Debug logging can append to `DEBUG_LOG` if configured. Daemonizing migrates the repository lock. No archive data is persisted by this module.

## Dependencies And Integration Points
Depends on `fuse_impl.hlfuse`, archive/matcher/filter helpers, `HardLinkManager`, msgpack, repository object parsing, uid/gid lookup, platform flags, and `daemonizing`. It is selected when `mfusepy` is preferred/available.

## Risks And Edge Cases
Path-based FUSE semantics differ from low-level APIs; offset handling in `readdir` currently yields repeated zero offsets, which may be sensitive to mfusepy expectations. Inode reuse for hard links mutates `DirEntry.ino`. Packed items save memory but require repeated msgpack unpacking. Versions mode uses SHA-256 truncated hashes, unlike `fuse.py`'s blake2b_128. `create` explicitly rejects writes with EROFS.

## Test Signals
Test through mfusepy-capable mount integration or backend unit tests for lazy expansion, path lookup, hard links, versions naming, xattrs, damaged chunks, handle release cache cleanup, readonly create, duplicate archive names, uid/gid/umask options, and debug logging.
