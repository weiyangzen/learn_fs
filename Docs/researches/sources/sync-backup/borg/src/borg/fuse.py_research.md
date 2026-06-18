# sources/sync-backup/borg/src/borg/fuse.py

## Purpose
Implements the low-level `borg mount` FUSE filesystem for llfuse or pyfuse3. It exposes one or more Borg archives as a read-only virtual filesystem, supports lazy archive expansion, optional versions mode, hard-link reconstruction, xattrs, symlink targets, damaged-file zero filling, and chunk-backed reads.

## Important APIs, Types, And Functions
`fuse_main()` dispatches to pyfuse3 under Trio or llfuse with `workers=1`. `async_wrapper()` presents synchronous methods as pyfuse3 coroutines when needed. `ItemCache` maps generated inode numbers to archive `Item` metadata using a dense bytearray plus a temporary file for metadata records that span chunks. `FuseBackend` constructs and resolves the virtual tree, with `_create_filesystem`, `_process_archive`, `_process_leaf`, `_process_inner`, `get_item`, and `check_pending_archive`. `FuseOperations` is the llfuse/pyfuse3 operation provider, implementing `mount`, `statfs`, `getattr`, `listxattr`, `getxattr`, `lookup`, `open`, `opendir`, `read`, `readdir`, and `readlink`.

## Control Flow
Mount setup parses mount options, validates forced uid/gid names, creates a default directory `Item`, builds the root, calls `llfuse.init`, optionally daemonizes, then runs the FUSE main loop under SIGUSR1/SIGINFO diagnostics. Without versions mode, archives are represented as placeholder directories and expanded on first lookup/opendir. `_process_archive` loads archive metadata chunks, filters by matcher and strip-components, creates implicit directories, installs leaves, and resolves hard links. File reads optimize linear access by remembering the last chunk position per file handle and caching partially read chunks.

## State And Persistence
State is in-memory except for `ItemCache.fd`, a process-local temporary file storing direct msgpack item records. Persistent repository data is read through `Repository.get_many`, `Repository.get`, and `manifest.repo_objs.parse`. `contents`, `parent`, `_items`, `pending_archives`, `versions_index`, inode caches, and data caches are rebuilt per mount. `mount()` migrates the repository lock when daemonizing.

## Dependencies And Integration Points
Depends on `Archive`, `Item`, `FuseVersionsIndex`, `HardLinkManager`, `LRUCache`, msgpack wrappers, repository object parsing, matcher/filter construction, platform uid/gid lookup, `daemonizing`, and FUSE bindings selected by `fuse_impl.py`. Kernel permission behavior is affected by `default_permissions`, `allow_other`, uid/gid/umask options, and Darwin `volname`.

## Risks And Edge Cases
The module explicitly assumes single-threaded synchronous access; pyfuse3 async reentrancy would be risky if true awaits are introduced. `ItemCache` has implicit inode offset/bytearray assumptions and can grow large for metadata-heavy archives. Lazy expansion can surprise memory use on directory traversal. Broken hard links are skipped with warnings. Missing repository chunks raise EIO unless `allow_damaged_files` is enabled, then reads return zero bytes. Symlinks may point outside the mount tree. Mount option parsing mutates a list and rejects unsupported typed values.

## Test Signals
Exercise through mount-focused integration tests where available: archive listing, lazy archive expansion, versions mode naming, duplicate archive name disambiguation, xattr lookup, symlink readlink, damaged chunk handling, hard-link nlink updates, uid/gid/umask mount options, pyfuse3/llfuse selection, and linear versus random read offsets.
