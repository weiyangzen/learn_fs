# File Research: sources/local-fs/ntfs-3g/libntfs-3g/dir.c

## Role

Implements NTFS directory handling: directory index names, lookup, pathname resolution, readdir, object creation, deletion, hard links, DOS-name extended attributes, parent lookup, and POSIX-style link-count calculation.

## Global Index Names

Defines little-endian NTFS index name constants:

- `NTFS_INDEX_I30` for directory filename indexes.
- `NTFS_INDEX_SII` and `NTFS_INDEX_SDH` for security indexes.
- `NTFS_INDEX_O`, `NTFS_INDEX_Q`, and `NTFS_INDEX_R` for object/reparse/quota-style indexes.

## Lookup and Caches

- `ntfs_inode_lookup_by_name()` searches a directory `$I30` B+tree for a Unicode filename. It searches index root first, then descends through index allocation blocks using child VCNs.
- `ntfs_inode_lookup_by_mbsname()` converts a multibyte name to Unicode and optionally uses the lookup cache.
- `ntfs_inode_update_mbsname()` updates the lookup cache after name changes.
- `ntfs_pathname_to_inode()` resolves a pathname from a supplied parent or the root directory, component by component, with optional inode path cache support.

When the volume is not case-sensitive, lookup normalizes cache keys through uppercase multibyte names and performs case-insensitive NTFS collation.

## Directory Enumeration

- `ntfs_interix_types()` decodes Interix special-file markers from unnamed data streams.
- `ntfs_dir_entry_type()` opens a referenced inode to classify reparse points, Interix special files, directories, and regular files.
- `ntfs_filldir()` converts an index entry into a caller callback, applying hidden/system metadata filtering and lowercasing names on case-insensitive mounts.
- `ntfs_mft_get_parent_ref()` finds the parent directory reference from the first resident `AT_FILE_NAME`.
- `ntfs_readdir()` emits synthetic `.` and `..`, scans `$INDEX_ROOT`, then scans in-use `$INDEX_ALLOCATION` blocks according to the `$BITMAP`.

## Creation

- `__ntfs_create()` allocates a new MFT record, builds `STANDARD_INFORMATION`, security descriptor state, directory `INDEX_ROOT` or file `DATA`, `FILE_NAME`, directory index entry, and optional WSL/Interix special-file metadata.
- `ntfs_create()`, `ntfs_create_device()`, and `ntfs_create_symlink()` are type-specific wrappers.

Creation inherits compression from the parent directory when NTFS version, cluster size, and mount options allow. Dotfiles can be hidden according to mount policy. WSL special files use reparse/EA helpers instead of Interix data markers.

## Delete and Link

- `ntfs_check_empty_dir()` verifies a directory has only the terminator entry in its root index.
- `ntfs_check_unlinkable_dir()` allows directory unlink only when empty or when link-count rules allow special hard-link cases.
- `ntfs_delete()` removes a name from the parent index and inode, handles DOS/WIN32 namespace pair deletion, invalidates caches, removes reparse/object-id index entries, frees non-resident clusters, frees extent records, and finally frees the base MFT record when link count reaches zero.
- `ntfs_link_i()` adds a `FILE_NAME` attribute and directory index entry, then increments link count.
- `ntfs_link()` creates a POSIX hard link.
- `ntfs_dir_parent_inode()` opens the parent directory inferred from the first filename attribute.

## DOS Name Extended Attributes

- `get_dos_name()` and `get_long_name()` inspect `FILE_NAME` attributes for DOS and long names in a specific parent directory.
- `ntfs_get_ntfs_dos_name()` returns the DOS name as an uppercased multibyte value.
- `set_namespace()` updates namespace flags in both the inode filename attribute and directory index entry.
- `set_dos_name()` coordinates adding/replacing DOS names and converting between POSIX, DOS, WIN32, and WIN32_AND_DOS filename namespaces.
- `ntfs_set_ntfs_dos_name()` validates and sets a short DOS name through xattr semantics.
- `ntfs_remove_ntfs_dos_name()` removes or demotes DOS-name state.

## Link Counts

- `ntfs_dir_link_cnt()` computes POSIX-visible link count. Directories are counted by scanning subdirectories plus `.`/`..`; regular files count non-DOS-only filename attributes.

## Dependencies

This file integrates most of libntfs-3g: attributes, inode/MFT allocation, indexes, NTFS time, cluster allocation, caches, security descriptors, reparse points, object IDs, xattrs, and EA helpers.

## Important Behavior

Directory lookup and readdir perform explicit bounds checks on index entries and index blocks. Delete intentionally keeps the last filename attribute in place when possible for undeletion behavior, unless it is in an extent. Many mutation paths close supplied inodes as part of their contract, especially delete and DOS-name xattr operations.

## Research Notes

`dir.c` is the high-level namespace manager for the library. It relies heavily on `index.c` for B+tree mutation and `ea.c`/reparse helpers for WSL special-file compatibility. Cache invalidation is scattered through delete/path operations and is conditional on compile-time cache sizes.
