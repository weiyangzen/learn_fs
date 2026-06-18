# File Research: sources/os/linux/linux-stable/fs/smb/client/dir.c

This file implements CIFS/SMB VFS dentry and directory-related operations: path construction, lookup, create/atomic open, mknod, tmpfile creation, negative/positive dentry validation, case-insensitive dentry operations, and silly-rename path generation.

Main responsibilities:
- Builds remote paths from dentries, optional DFS tree prefixes, mount prepaths, and CIFS path separators.
- Validates filename component length and rejects backslash in POSIX-disallowed mounts.
- Implements file creation and create+open through `__cifs_do_create()`, `cifs_do_create()`, `cifs_atomic_open()`, and `cifs_create()`.
- Supports legacy POSIX open when available, normal SMB open otherwise, and post-create inode metadata lookup.
- Handles fscache read-around requirements by requesting read access for write-only opens when needed.
- Uses cached parent directory handles to set SMB2 parent lease keys and invalidate cached dirents.
- Implements `cifs_lookup()` with cached negative lookup shortcuts, POSIX/Unix/standard inode query paths, and retry on `-EAGAIN`.
- Implements dentry revalidation via `cifs_d_revalidate()` for positive and negative dentries.
- Provides case-insensitive hash/compare operations using the mount NLS table.
- Implements SMB2+ `O_TMPFILE` by creating hidden temporary names with delete-on-close semantics and setting temporary/hidden attributes.
- Generates silly-rename full paths for deferred delete behavior.

Important flows:
- Path construction: `build_path_from_dentry()` delegates to optional-prefix helper and may prepend DFS tree name and prepath before converting separators.
- Create/open: `cifs_atomic_open()` checks forced shutdown, resolves tlink, validates name, creates lease key, records pending open, calls `cifs_do_create()`, instantiates/splices dentry, finishes open, creates `cifsFileInfo`, and starts fscache cookie use.
- Lookup: `cifs_lookup()` checks name validity, builds full path, optionally trusts valid cached directory negative state, queries inode info, renews parent timestamps on success, and returns `d_splice_alias()`.
- Revalidation: positive dentries call `cifs_revalidate_dentry()` and handle deleted/stale cases; negative dentries may remain valid if the parent cached directory is valid.
- Tmpfile: `cifs_tmpfile()` creates a unique hidden name under the parent, marks inode link count zero, instantiates the unhashed dentry, opens file state, then sets hidden/temporary attributes.

Concurrency and lifetime:
- Tcon links are acquired through `cifs_sb_tlink()` and released after each operation.
- Dentry path buffers are allocated with `alloc_dentry_path()` and freed after use.
- Pending opens are added before create/open and removed on failure.
- Cached directory handles are opened/closed around validation checks.

External dependencies:
- Calls server dialect operations for open, close, make_node, set_file_info, and lease-key handling.
- Uses inode query helpers from CIFS core.
- Integrates with fscache, cached directory support, POSIX extensions, and legacy CIFS Unix extensions.

Research notes:
- This file is the main VFS dentry bridge between Linux path semantics and SMB path/open operations.
- Negative dentry caching is conservative unless the parent directory cache is known valid.
- Case-insensitive operations depend on the mount codepage and CIFS uppercase conversion.
