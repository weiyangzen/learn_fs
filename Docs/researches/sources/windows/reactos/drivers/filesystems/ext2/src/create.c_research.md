# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/create.c

This is the main create/open path for files, directories, symlinks, and volume opens. It performs Windows create-disposition policy, ext namespace lookup, symlink following, inode creation, EA replacement, share/oplock checks, cache setup, delete-on-close setup, and supersede/overwrite handling.

Key functions:
- `Ext2IsNameValid`: rejects invalid Windows filename characters such as `|`, `:`, `/`, `*`, `?`, `"`, `<`, and `>`.
- `Ext2FollowLink`: reads inline or block-backed symlink contents, converts `/` to `\`, converts OEM to Unicode, recursively looks up the target with depth/stack guards, and updates Mcb symlink/special state and target references.
- `Ext2IsSpecialSystemFile`: identifies root-level Windows special files/directories such as `pagefile.sys`, `swapfile.sys`, `hiberfil.sys`, `Recycled`, `RECYCLER`, and `$RECYCLE.BIN`.
- `Ext2LookupFile`: resolves a Unicode path relative to a parent or root MCB, uses the MCB cache first, scans directories on cache miss, allocates/loads new MCBs, sets file attributes from inode mode/access, follows symlinks unless disabled, and returns a referenced MCB.
- `Ext2ScanDir`: builds a dentry for a child name and calls `ext3_find_entry` to find the on-disk directory entry and inode number.
- `Ext2AddDotEntries`: after creating a directory, appends and initializes `.` and `..` entries, sets link count, dirties the buffer, and marks the inode dirty.
- `Ext2OverwriteEa`: validates a Windows EA buffer, obtains an ext4 xattr ref, purges existing user xattrs, validates EA names, and writes EA values through `ext4_fs_set_xattr`.
- `Ext2CreateFile`: the main file create/open state machine. It parses create options/disposition, resolves parent and target names, creates missing files/directories when allowed, opens target directories for rename semantics, handles symlink reparse-point options, checks ext access, allocates/reuses FCBs and CCBs, checks oplocks/share access, sets cache and section pointers, handles delete-on-close, creates directory dot entries, overwrites EAs, emits notifications, and handles supersede/overwrite.
- `Ext2CreateVolume`: handles direct volume opens, share access, volume locking when opened exclusively, cache flushing for raw/noncached access, and VCB open/reference counts.
- `Ext2Create`: dispatch entry for `IRP_MJ_CREATE`; handles the filesystem device object, verifies mount/VCB state, rejects locked/dismounting volumes, and routes to volume or file create.
- `Ext2CreateInode`: allocates an inode near the parent group, initializes owner/group/mode/timestamps/generation/extra inode size, initializes extents when supported, saves the inode, and adds the directory entry.
- `Ext2SupersedeOrOverWriteFile`: purges cache, truncates/expands allocation, resets sizes, updates timestamps/inode size, saves the inode, and overwrites EAs.

Research notes:
- The function has careful reference choreography around MCBs, FCBs, CCBs, and symlink targets; most failures unwind in the `finally` block.
- The path resolver uses `Vcb->McbLock`, while create/open FCB allocation uses `Vcb->FcbLock` and then per-FCB main resources.
- Ext4 extent support is forced for new inodes when the superblock has `EXT4_FEATURE_INCOMPAT_EXTENTS`.
- `FILE_OPEN_BY_FILE_ID` is explicitly not implemented.
