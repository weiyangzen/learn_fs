# File Research: sources/os/linux/linux/fs/ufs/namei.c

## Purpose
Implements UFS directory inode operations for Linux VFS name lookup and namespace mutation: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## Main Contents
- `ufs_add_nondir()`: common helper that adds a directory entry for non-directories, instantiates the dentry on success, and discards the new inode on failure.
- `ufs_lookup()`: validates `UFS_MAXNAMLEN`, resolves inode numbers through `ufs_inode_by_name()`, and returns aliases via `d_splice_alias()`.
- Creation paths:
  - `ufs_create()` allocates a regular inode and attaches file inode/file/address-space ops.
  - `ufs_mknod()` validates old device encoding, initializes special inode metadata, and stores UFS-specific device data.
  - `ufs_symlink()` chooses slow page-cache symlinks or fast in-inode symlinks based on `s_maxsymlinklen`.
  - `ufs_mkdir()` handles parent/child link counts, initializes an empty directory, and links it into the parent.
- Removal and movement:
  - `ufs_unlink()` finds and deletes the directory entry, then drops the target link count.
  - `ufs_rmdir()` checks emptiness before unlinking and adjusts directory link counts.
  - `ufs_rename()` supports only `RENAME_NOREPLACE`, handles directory `..` updates, replacement targets, and link count adjustments.
- Exports `ufs_dir_inode_operations`.

## Important Design Points
- Closely follows ext2-style VFS namei patterns while relying on UFS directory helpers from `dir.c`.
- Directory rename has separate handling for moving directories across parents because `..` must be updated with `ufs_set_link()`.
- Fast symlinks store bytes in `UFS_I(inode)->i_u1.i_symlink`; slow symlinks use page-cache-backed symlink operations.
- Error paths are mostly link-count centered: newly allocated inodes are discarded, and parent directory link increments are undone.

## Cross-File Relationships
- Uses on-disk constants from `ufs_fs.h`, internal inode/super helpers from `ufs.h`, and device helpers from `util.h`.
- Calls directory helpers declared in `ufs.h`: `ufs_add_link()`, `ufs_find_entry()`, `ufs_delete_entry()`, `ufs_empty_dir()`, `ufs_make_empty()`, `ufs_dotdot()`, and `ufs_set_link()`.
- Uses inode allocation and loading APIs from other UFS files: `ufs_new_inode()` and `ufs_iget()`.
- File, directory, and address-space operation tables are declared in `ufs.h` and installed here for newly created inodes.

## Risks / Review Notes
- `ufs_symlink()` rejects links larger than one filesystem block before deciding fast versus slow symlink.
- Rename semantics are intentionally limited: unsupported flags other than `RENAME_NOREPLACE` return `-EINVAL`.
- Directory replacement paths must preserve link-count invariants; changes in `ufs_rename()` need careful audit against VFS rename locking assumptions.
