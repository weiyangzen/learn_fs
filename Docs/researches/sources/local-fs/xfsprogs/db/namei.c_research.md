# File Research: sources/local-fs/xfsprogs/db/namei.c

## Purpose
Implements path navigation, directory listing, parent-pointer listing, and expert directory entry creation/removal for xfs_db.

## Main Interfaces
- `namei_init()` registers `path`, `ls`/`l`, and `parent`/`pptr`; in expert mode it also registers `link` and `unlink`.
- Exports `path_walk()` and `listdir()` for other db code.
- Defines `dir_emit_t` callback contract in the header.

## Path And Listing Flow
`path_parse()` splits paths into components, ignoring repeated slashes. `path_walk()` starts absolute paths at a supplied root inode, relative paths at the current directory cursor, and delegates to `path_navigate()`, which repeatedly igets directories and calls `libxfs_dir_lookup` before setting the cursor to the target inode. `listdir()` detects shortform, block, leaf, and node directory formats and emits entries through callback traversal. `ls` can list current or named paths and can print inode numbers only.

## Parent Pointers
`parent` lists XFS parent-pointer attributes when the feature is enabled. It handles shortform, leaf, and node attr formats, walks attr leaves including right siblings, decodes parent records with `libxfs_parent_from_attr`, and prints parent inode/generation plus the stored name.

## Expert Mutations
`link` creates a directory entry in the current directory pointing to an inode or path, sets/derives file type, updates link counts, fixes child `..` for directories, and adds parent-pointer records when enabled. `unlink` looks up an entry in the current directory, drops link counts, removes the dirent, and removes the parent pointer in a transaction.

## Dependencies
Uses libxfs directory, attr, parent-pointer, transaction, and inode APIs; xfs_db IO cursor and type state; command/input/output helpers; and mount feature predicates.

## Risks And Invariants
- Relative path walking requires the current cursor to be a directory inode.
- Directory listing has separate logic for shortform, block, leaf, and node formats; corrupt layout returns errors or stops traversal.
- Link/unlink are expert-only because they mutate directory metadata and parent-pointer state.
