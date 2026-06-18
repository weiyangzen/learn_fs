# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/ext3/recover.c

This file handles ext3 journal discovery and recovery during mount/open processing. It is a small bridge between Ext2Fsd volume state and the bundled Linux-style JBD journal implementation.

`Ext2LoadInternalJournal` allocates an Mcb for the journal inode, assigns the supplied inode number to `Jcb->Inode.i_ino`, binds it to the VCB superblock, and loads it with `Ext2LoadInode`. On load failure it frees the Mcb and returns `NULL`. `Ext2CheckJournal` inspects the ext3 superblock stored in `Vcb->SuperBlock`. If `EXT3_FEATURE_INCOMPAT_RECOVER` is set, it marks `VCB_JOURNAL_RECOVER`; it refuses recovery for read-only volumes, external journal configurations (`s_journal_inum == 0` or `s_journal_dev`), and otherwise returns the internal journal inode number.

`Ext2RecoverJournal` serializes recovery under `Vcb->MainResource`, validates the journal with `Ext2CheckJournal`, loads the internal journal inode, initializes a `journal_t` via `journal_init_inode`, and calls `journal_load`. After attempting replay it refreshes the superblock and group descriptors with `Ext2RefreshSuper` and `Ext2RefreshGroup`. On successful replay it wipes recovery records, clears `EXT3_FEATURE_INCOMPAT_RECOVER`, saves the superblock, syncs the block device, and clears `VCB_JOURNAL_RECOVER`.

Cleanup is explicit: the journal object is destroyed with `journal_destroy`, the journal Mcb is freed with `Ext2FreeMcb`, and `MainResource` is released. Return values are negative internal error codes for distinct failure stages rather than NTSTATUS. The implementation only supports internal journals and intentionally stops before replay on read-only volumes.
