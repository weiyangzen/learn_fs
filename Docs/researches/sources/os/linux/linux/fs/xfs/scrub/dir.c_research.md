# File Research: sources/os/linux/linux/fs/xfs/scrub/dir.c

## Role
Scrubs XFS directory metadata. It validates directory DA tree records, data/free-space accounting, all directory entries, inode targets, file-type fields, and parent pointer backreferences when enabled.

## Setup
- `xchk_setup_directory` optionally initializes repair support through `xrep_setup_directory`, then calls `xchk_setup_inode_contents`.

## Directory Entry Validation
- `xchk_dir_actor` is called by `xchk_dir_walk` for each dirent.
- Checks inode number validity, name validity, `.` and root `..` consistency, hash lookup consistency, child inode existence, file type correctness, and metadir/non-metadir tree separation.
- Uses `xchk_iget` for child inode references and records child inode corruptions as xref problems where appropriate.

## Parent Pointer Checking
- `xchk_dir_check_pptr_fast` skips `.`/`..`, rejects non-dot self references, and tries to lock child IOLOCK/ILOCK without waiting.
- If child locks cannot be obtained, the dirent name and inode are stashed in `xfarray`/`xfblob`.
- `xchk_dir_finish_slow_dirents` later revalidates deferred dirents and performs slower parent pointer checks, cycling locks if needed.

## DA Tree and Leaf Record Checks
- `xchk_da_btree` is used with `xchk_dir_rec`.
- `xchk_dir_rec` validates leaf hash order, leaf address pointers, referenced data block bounds, data entry presence, data entry tag, inode number, nonzero name length, and recomputed name hash.

## Free-Space Checks
- `xchk_directory_data_bestfree` validates bestfree entries inside data/block-format directory blocks and ensures free entries correspond to bestfree accounting.
- `xchk_directory_leaf1_bestfree` checks leaf1 tail bestfree arrays, leaf hash order, stale counts, and data-block bestfree values.
- `xchk_directory_free_bestfree` checks free-space index blocks for consistency with data blocks.
- `xchk_directory_blocks` walks the directory data fork extents to invoke the correct free-space checks for block, leaf, and node formats.

## Top-Level Scrub
- `xchk_directory` rejects non-directories, zapped directories, and implausibly small sizes.
- Runs DA tree checks, free-space checks, full readdir/name checks, and deferred parent-pointer checks.
- Marks the directory-zapped health bit healthy if no corruption is found.

## Zapped Directory Detection
- `xchk_dir_looks_zapped` identifies directories whose data fork was explicitly zapped or reset to empty extents format, in which case higher-level checks should defer until repair rebuilds mappings.
