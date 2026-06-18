# File Research: sources/local-fs/xfsdump/restore/tree.c

## Summary
Implements xfsrestore’s persistent directory tree model. It ingests dumped directories and entries, tracks hard links and subtree selections, resolves paths, creates/removes/renames directories, drives non-directory restore callbacks, restores directory metadata, and manages the restore orphanage.

## Main Responsibilities
- Create or resync the `tree` housekeeping file.
- Allocate persistent tree nodes through `node.c` and index them by inode/generation through a persistent hash array.
- Maintain parent/child/sibling relationships and hard-link lists.
- Track node state with flags for real filesystem objects, selected subtrees, references, written files, directories, dumped directories, and new orphans.
- Build and maintain an `orphanage` directory under the restore destination.
- Apply directory dump records through `tree_begindir()` and `tree_addent()`.
- Post-process restored directory state by removing unreferenced entries, creating missing directories, renaming directories, and processing hard links.
- Select subtrees from command-line paths or interactive commands and synchronize selection with `inomap`.
- Walk hard-link lists to invoke file restore/link callbacks.
- Restore directory attributes, timestamps, ownership, mode, and XFS project/extent flags.
- Provide optional tree consistency checks under `TREE_CHK`.

## Core State
`treepers_t` persists root inode, root node handle, orphanage node handle, hash sizing, restore ownership/full-dump flags, orphan-handling mode, and generation-number compatibility mode.

`tran_t` stores transient restore context: housekeeping and destination paths, orphanage path, destination-XFS flag, persistent fd, mapped hash array, temporary name buffer, and interactive dialog state.

Each `node_t` represents a directory entry or hard-link entry with inode, name-registry handle, directory-attribute handle, hash link, parent/sibling/child links, hard-link link, generation, and flags.

## Important Behavior
`tree_init()` creates the orphanage directory, creates and maps the persistent tree file, initializes the hash and node abstractions, creates root and orphanage nodes, links them into the hash, and adopts orphanage under root.

`tree_sync()` reopens persisted tree state, recreates the orphanage if needed, remaps the hash and node abstractions, and updates the current full-dump mode.

`tree_check_dump_format()` prevents applying old format-2 generation-number dumps after a restore has already begun in format-3-or-newer mode unless compatibility truncation was enabled from the start.

`tree_begindir()` handles a directory header. It finds an existing hard-link head by inode/generation, upgrades prior non-directory placeholders to directories, refreshes directory attributes, or creates new orphaned directory nodes until a parent entry adopts them.

`tree_addent()` handles directory entries. It updates existing directories, records pending directory renames in `n_lnkh`, retains or creates non-directory hard-link nodes, reserves the root-level `orphanage` name, and marks referenced entries.

`tree_post()` runs the post-directory pass: remove or orphan unreferenced entries for incremental restores, create missing directories, rename directories out of orphanage, and process hard links.

`tree_cb_links()` is called for each non-directory inode. It resolves all selected hard-link paths, enforces overwrite policy, unlinks stale existing files before restore when needed, invokes the caller callback to restore the first path and link later paths, and creates orphanage entries for unreferenced file data.

`tree_adjref()` propagates reference state through unchanged-but-referenced directories, based on whether parent directories were dumped.

`tree_subtree_parse()`, `tree_markallsubtree()`, `selsubtree()`, and `selsubtree_recurse_down()` manage selected restore subtrees and update `inomap` for non-directory restore inclusion.

`tree_subtree_inter()` implements the interactive selector with `pwd`, `ls`, `cd`, `add`, `delete`, `extract`, `quit`, and `help` commands.

`Node2path()` recursively builds restore paths from parent links. Nodes under orphanage are named as `ino.gen`; the orphanage node itself is named `orphanage`.

`setdirattr()` restores times, mode, optional owner/group, and XFS-specific `fsxattr` values using handle APIs when the destination is XFS.

`hash_*()` implements a power-of-two inode hash table whose entries point to hard-link-list heads. `link_*()` layers hard-link list operations on top of that hash.

`parse()` is a small shell-like tokenizer for the interactive dialog, supporting quotes, backslash escapes, hex/octal escapes, and whitespace collapsing.

## Dependencies
Depends on restore content and inode headers, `inomap`, `namreg`, `dirattr`, `node`, `bag`, dialog/logging/control helpers, path/open utilities, XFS handle and ioctl APIs, POSIX filesystem operations, and global restore policy such as `restore_rootdir_permissions` and `need_fixrootdir`.

## Risks
This file is the restore metadata coordinator; corruption in node links, hash entries, name handles, or directory-attribute handles can affect deletion, rename, hard-link creation, and final path resolution.

Many invariants are enforced by assertions, including node relationships, name handles, generation handling, and tree layout. Release builds may not stop on malformed state.

`Node2path_recurse()` uses recursion and a thread-local parent-path cache. Very deep directory trees risk recursion depth and pathname-length failures.

The orphanage is a real directory named `orphanage` in the destination root, so the code reserves that name and warns or fails when it collides with existing user content.

Incremental restore behavior is complex: unreferenced real entries may be unlinked, renamed into orphanage, retained, or used as hard-link sources depending on flags and hard-link lists.

`setdirattr()` may attempt XFS-specific handle operations and later use `fd` for `XFS_IOC_FSSETXATTR`; failures are logged, but metadata restoration may be partial.

The interactive parser mutates its input buffer in place and uses custom escape handling, so command parsing is not equivalent to a full shell parser.
