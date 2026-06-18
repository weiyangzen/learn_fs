# File Research: sources/os/linux/linux/fs/overlayfs/copy_up.c

## Role

Implements OverlayFS copy-up: creating an upper object from a lower object when write, metadata update, indexing, metacopy, or export semantics require it.

## Main Responsibilities

- Provides obsolete `check_copy_up` module parameter compatibility.
- Copies xattrs and ACLs from lower to upper while ignoring OverlayFS private xattrs and respecting LSM `security_inode_copy_up_xattr()`.
- Copies file attributes, storing immutable/append-only protection in OverlayFS xattrs when needed.
- `ovl_copy_up_file()` tries `vfs_clone_file_range()` first, then falls back to chunked `do_splice_direct()` copying with `SEEK_DATA` sparse-hole optimization.
- Sets size, mode, ownership, timestamps, origin file handles, metacopy xattrs, and optional metadata fsync.
- Encodes lower/upper file handles for origin and index metadata.
- Creates index entries for copied-up directories and links indexed non-directories through index paths.
- Supports two creation strategies: workdir temporary object plus rename, or `O_TMPFILE` plus link.
- Implements metadata-only copy-up and later data copy-up for metacopy files.
- Public wrappers are `ovl_maybe_copy_up()`, `ovl_copy_up_with_data()`, and `ovl_copy_up()`.

## Important Control Flow

`ovl_copy_up_flags()` verifies lower data, climbs to the highest ancestor needing copy-up, and calls `ovl_copy_up_one()` under overlay credentials. `ovl_copy_up_one()` gathers lower stat data, decides whether metadata fsync and metacopy are needed, handles symlink targets, then serializes with `ovl_copy_up_start()`.

`ovl_do_copy_up()` decides whether indexing is required, prepares origin file handles, chooses destination directory/name, marks parent directories impure when needed, then dispatches to tmpfile or workdir copy-up. After success, it updates inode flags such as `OVL_INDEX`, `OVL_UPPERDATA`, digest flags, whiteouts, and dentry revalidation state.

## Data and Security Notes

Credential override uses `security_inode_copy_up()` so LSMs can provide copy-up credentials. Metacopy with required verity falls back to full copy if lower data lacks active fs-verity.

## Dependencies

Deeply tied to `overlayfs.h` helpers, xattr wrappers, indexdir/workdir management, file handle encoding, VFS copy/clone/splice APIs, fs-verity, and overlay inode flags.

## Research Notes

This is one of OverlayFS’s central correctness files. It preserves identity, metadata, sparse data, security labels, and copy-up atomicity while avoiding problematic lock ordering in nested overlays.
