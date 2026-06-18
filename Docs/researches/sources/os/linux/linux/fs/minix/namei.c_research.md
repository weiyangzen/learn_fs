# File Research: sources/os/linux/linux/fs/minix/namei.c

## Purpose
Implements Minix directory inode operations for lookup, create, link, unlink, symlink, mkdir, rmdir, rename, mknod, and tmpfile.

## Main Responsibilities
- Connect Minix directory-entry helpers to the Linux VFS inode operations table.
- Allocate and initialize new Minix inodes for files, directories, symlinks, special files, and tmpfiles.
- Maintain link counts for hard links and directories.
- Update directory entries for unlink and rename.
- Validate Minix name length and basic link-count corruption conditions.

## Key Functions
- `add_nondir()` adds a directory link for a non-directory inode and instantiates the dentry; on failure it decrements the inode link count and drops the inode.
- `minix_lookup()` validates name length, resolves inode number with `minix_inode_by_name()`, and returns `d_splice_alias()`.
- `minix_mknod()` checks old device-number validity, allocates an inode, calls `minix_set_inode()`, marks it dirty, and links it.
- `minix_tmpfile()` creates an unlinked inode and attaches it to a tmpfile.
- `minix_create()` delegates to `minix_mknod()` with `rdev = 0`.
- `minix_symlink()` rejects symlink bodies larger than one filesystem block, creates a symlink inode, and stores the body with `page_symlink()`.
- `minix_link()` increments source link count, takes an inode reference, and adds a new directory entry.
- `minix_mkdir()` creates directory inode, increments parent and child link counts, writes `.`/`..`, and links the new directory.
- `minix_unlink()` finds and deletes the directory entry, then decrements target link count.
- `minix_rmdir()` requires an empty directory, then unlinks it and adjusts parent/child link counts.
- `minix_rename()` handles rename with and without replacement, directory `..` updates, empty-target checks, and link-count adjustment.
- `minix_dir_inode_operations` exports the operation table.

## Data and Control Flow
Most create-like operations allocate an inode through `minix_new_inode()`, initialize operations with `minix_set_inode()`, mark the inode dirty, then add a directory entry. Remove-like operations find a Minix directory entry and operate on the mapped folio before releasing it with `folio_release_kmap()`.

Rename first finds the old entry, optionally finds the old directory’s `..` entry, validates replacement target rules, updates or adds the target entry, deletes the old entry, and if moving a directory updates its `..` entry to the new parent.

## Important Behaviors and Edge Cases
- Names longer than the mounted Minix name limit return `-ENAMETOOLONG`.
- `minix_mknod()` rejects device numbers not representable by old device encoding.
- Symlink targets must fit in one block.
- `minix_unlink()` and `minix_rmdir()` detect corrupted zero/low link counts and report filesystem corruption.
- Rename supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Directory replacement during rename requires the target directory to be empty and have valid link count.
- Moving a directory increments the new parent link count before deleting the old link and updates `..`.

## Dependencies
- Directory-entry helpers declared in `minix.h`, implemented in sibling Minix directory code.
- VFS inode/dentry helpers such as `d_instantiate()`, `d_splice_alias()`, `page_symlink()`, and link-count helpers.
- Minix inode initialization from `inode.c`.

## Research Notes
This is a compact, traditional filesystem `namei` implementation. It relies on the VFS for higher-level permission checks; the file itself mostly performs filesystem-specific entry manipulation and integrity checks.
