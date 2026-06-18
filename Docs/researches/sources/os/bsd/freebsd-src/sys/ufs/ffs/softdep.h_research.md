# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/softdep.h

## Purpose
Defines the private soft updates and soft-update journaling dependency model used by FFS. This header is a structural map of metadata dependency objects, state flags, work queues, journaling dependencies, hash tables, and per-mount softdep state.

## Key Contents
- Dependency state flags:
  - `ATTACHED`, `UNDONE`, `COMPLETE`, `DEPCOMPLETE`
  - Directory-specific flags: `MKDIR_PARENT`, `MKDIR_BODY`, `RMDIR`, `DIRCHG`
  - Lifecycle/write flags: `GOINGAWAY`, `IOSTARTED`, `DELAYEDFREE`, `NEWBLOCK`, `INPROGRESS`, `ONWORKLIST`, `IOWAITING`, `ONDEPLIST`, `WRITESUCCEEDED`
  - UFS/journal flags: `UFS1FMT`, `EXTDATA`
  - Unlinked-inode tracking: `UNLINKED`, `UNLINKNEXT`, `UNLINKPREV`, `UNLINKONLIST`, `UNLINKLINKS`
  - Completion mask: `ALLCOMPLETE`
- Dependency type identifiers:
  - `D_PAGEDEP`, `D_INODEDEP`, `D_BMSAFEMAP`, `D_NEWBLK`, `D_ALLOCDIRECT`, `D_INDIRDEP`, `D_ALLOCINDIR`
  - Freeing/removal types: `D_FREEFRAG`, `D_FREEBLKS`, `D_FREEFILE`, `D_FREEWORK`, `D_FREEDEP`
  - Directory types: `D_DIRADD`, `D_MKDIR`, `D_DIRREM`, `D_NEWDIRBLK`
  - Journal types: `D_JADDREF`, `D_JREMREF`, `D_JMVREF`, `D_JNEWBLK`, `D_JFREEBLK`, `D_JFREEFRAG`, `D_JSEG`, `D_JSEGDEP`, `D_JTRUNC`, `D_JFSYNC`
  - `D_SBDEP`, `D_SENTINEL`
- Common work item:
  - `struct worklist`
  - Must be first field in dependency structures that participate in work queues.
  - Carries mount pointer, type, state, global list linkage, and invariant debug provenance.
- Type conversion macros:
  - `WK_PAGEDEP`, `WK_INODEDEP`, `WK_BMSAFEMAP`, `WK_NEWBLK`, etc.
- Dependency list heads:
  - Defines many `LIST_HEAD`/`TAILQ_HEAD` collections for directory, inode, block, journal, and free-work dependencies.
- Core dependency structures:
  - `struct pagedep`: tracks directory page dependencies, pending adds/removes, move-reference journal records, and new directory blocks.
  - `struct inodedep`: tracks dependencies tied to an inode write, including delayed operations, allocation updates, link changes, unlinked list state, and rollback snapshots.
  - `struct bmsafemap`: tracks dependencies waiting on a cylinder group bitmap write.
  - `struct newblk`: generic newly allocated block dependency.
  - `struct allocdirect`: direct inode block pointer allocation dependency.
  - `struct indirdep`: indirect block dependency manager with safe copy/live copy handling.
  - `struct allocindir`: indirect pointer allocation dependency.
  - `union allblk`: allocation sizing union for `newblk`, `allocdirect`, and `allocindir`.
  - `struct freefrag`: delayed fragment free after fragment replacement.
  - `struct freeblks`: root object for truncation/freeing file block trees.
  - `struct freework`: child work items for freeing direct/indirect block trees.
  - `struct freedep`: bitmap-write completion dependency for frees.
  - `struct freefile`: delayed inode free after zero-link inode is safely written.
  - `struct diradd`, `struct mkdir`, `struct dirrem`, `struct newdirblk`: directory mutation dependency records.
- Journal dependency structures:
  - `struct inoref`: common reference operation payload.
  - `struct jaddref`: journals new references.
  - `struct jremref`: journals removed references.
  - `struct jmvref`: journals directory entry offset movement.
  - `struct jnewblk`: journals newly allocated blocks/fragments.
  - `struct jblkdep`, `struct jfreeblk`, `struct jfreefrag`: journal block-free dependencies.
  - `struct jtrunc`: journals truncation intent.
  - `struct jfsync`: journals fsync completion.
  - `struct jsegdep`: reference to a written journal segment.
  - `struct jseg`: journal segment write state.
  - `struct jblocks` and `struct jextent`: journal extent allocator and sequence tracking.
- Superblock dependency:
  - `struct sbdep`: tracks superblock writes for the soft-update journal unlinked inode list head.
- Hash and per-mount structures:
  - Hash heads for `pagedep`, `inodedep`, `newblk`, `bmsafemap`, and indirect freework.
  - `struct mount_softdeps`: all per-filesystem softdep state, including locks, pending work queues, journal queues, dirty cylinder groups, unlinked inode list, hash tables, counters, flush thread state, and per-type dependency lists.
- Flush thread flags:
  - `FLUSH_EXIT`, `FLUSH_CLEANUP`, `FLUSH_STARTING`, `FLUSH_RC_ACTIVE`, `FLUSH_DI_ACTIVE`
- Compatibility macros:
  - Maps old `ufsmount` field names to `um_softdep->sd_*` fields.

## Interactions
- Consumed by the FFS soft updates implementation.
- Coupled to UFS directory, inode, cylinder group, block allocation, truncation, and journaling code.
- Structures mirror journal record formats declared in `ffs/fs.h`.
- `ufs_extern.h` exposes selected softdep setup/revert functions used by UFS directory and vnode operations.
