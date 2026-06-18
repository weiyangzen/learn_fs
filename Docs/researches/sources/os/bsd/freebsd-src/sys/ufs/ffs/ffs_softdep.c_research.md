# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_softdep.c

This report was synthesized from ordered chunk research outputs.

## Chunk Map

- chunk 1: lines 1-8878, source bytes 262108, report `Docs/researches/chunks/chunk_sources_os_bsd_freebsd_src_sys_ufs_ffs_ffs_softdep_c_1_1_8878_8237500410aa_research.md`
- chunk 2: lines 8879-15020, source bytes 176949, report `Docs/researches/chunks/chunk_sources_os_bsd_freebsd_src_sys_ufs_ffs_ffs_softdep_c_2_8879_15020_27b5e3ebbd0b_research.md`

## Chunk Research

### Chunk 1: lines 1-8878

# Chunk Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_softdep.c lines 1-8878

## Scope

This chunk covers the opening 8,878 lines of FreeBSD FFS soft updates and soft updates journaling support. It includes the non-`SOFTUPDATES` stubs, active softdep feature registration, dependency allocation/accounting, per-mount initialization and teardown, worklist and journal queue infrastructure, journal segment writing/completion, allocation bitmap dependencies, direct and indirect block allocation dependencies, block/inode deallocation setup, truncation machinery, and the beginning of directory-entry addition handling. The chunk ends in the signature and comments for `softdep_change_directoryentry_offset()`, whose implementation continues in the next chunk.

## APIs and Entry Points

- Non-`SOFTUPDATES` build stubs export the same public softdep API surface, mostly panicking on impossible calls and returning no-op status for selected hooks such as `softdep_mount()`, `softdep_initialize()`, `softdep_fsync()`, `softdep_flushworklist()`, cleanup requests, journal lookup, and dependency counts.
- Active exported entry points in this chunk include `softdep_initialize()`, `softdep_uninitialize()`, `softdep_mount()`, `softdep_unmount()`, `softdep_flushfiles()`, `softdep_flushworklist()`, `softdep_prealloc()`, `softdep_prerename()`, `softdep_prelink()`, `softdep_journal_lookup()`, `softdep_setup_inomapdep()`, `softdep_setup_blkmapdep()`, `softdep_setup_allocdirect()`, `softdep_setup_allocext()`, `softdep_setup_allocindir_page()`, `softdep_setup_allocindir_meta()`, `softdep_journal_freeblocks()`, `softdep_journal_fsync()`, `softdep_setup_freeblocks()`, `softdep_freefile()`, and `softdep_setup_directory_add()`.
- Active internal hooks assigned to `bioops` are declared here: `softdep_disk_io_initiation()`, `softdep_disk_write_complete()`, `softdep_deallocate_dependencies()`, and `softdep_count_dependencies()`. Their bodies are later in the file.
- The per-filesystem flush thread entry point is `softdep_flush()`, created by `softdep_mount()` and stopped by `softdep_unmount()`.
- SUJ journal APIs in this chunk include `journal_mount()`, `journal_unmount()`, `journal_space()`, `journal_suspend()`, `journal_unsuspend()`, `softdep_process_journal()`, `softdep_flushjournal()`, `jwait()`, and record writers for add/remove/move references, new/free blocks, truncation, and fsync.
- Directory-add setup begins with `setup_newdir()` and `softdep_setup_directory_add()`. The next public directory helper, `softdep_change_directoryentry_offset()`, starts at the chunk boundary and must be read in the next chunk.

## Control Flow

Initialization installs global softdep BIO hooks, initializes the global mount list and callout, sets `max_softdeps`, and registers an AST cleanup callback. Mount setup allocates `mount_softdeps`, initializes hash tables and dependency lists, enables `MNT_SOFTDEP`, optionally opens and validates the SUJ journal file, starts a per-mount `softdepflush` thread, and may recompute cylinder group summaries if `vfs.ffs.compute_summary_at_mount` is enabled for an unclean filesystem. Unmount reverses these steps, stops the flush thread, unmounts the journal, removes the mount from the global list, asserts all dependency lists are drained, destroys hashes and locks, and frees mount state.

The background work loop calls `softdep_process_worklist()` until no work remains or journal suspension forces more processing. Worklist processing first flushes journal records, then pulls FIFO-ish items from `softdep_workitem_pending` using a sentinel and dispatches only the visible background work types: directory removals, block frees, fragment frees, and inode frees. `process_removes()` and `process_truncates()` are vnode-local pressure paths used when locked vnodes prevent the normal flusher from reclaiming journal space.

SUJ flow reserves journal space before allocations and link-count changes. `softdep_prealloc()`, `softdep_prerename()`, and `softdep_prelink()` flush vnode work, process removes/truncates, wake flushers, and may return `ERELOOKUP` after dropping vnode locks. When low journal space persists, `journal_check_space()` can sync metadata and eventually call `journal_suspend()` to set `MNTK_SUSPEND`; `journal_unsuspend()` resumes writes once space crosses the minimum threshold.

Journal work is queued with `add_to_journal()`. `softdep_process_journal()` packs pending records into one or more `jseg` buffers, writes a segment header at each device block boundary, allocates journal disk space from `jblocks`, writes the buffer, and optionally issues a BIO flush barrier. Completion is deliberately ordered: `handle_written_jseg()` marks a segment dependency complete, `softdep_synchronize_completed()` marks flushed segments complete, and `complete_jsegs()` only completes segments in write order before reclaiming older journal space through `free_jsegs()`.

Allocation setup is staged. Cylinder group bitmap updates create `bmsafemap` plus `inodedep` or `newblk` records. Later pointer updates convert `newblk` to `allocdirect` or `allocindir` and attach those structures to file buffers, indirect buffers, inode dependency lists, and journal records. Allocation merge paths collapse repeated fragment/block upgrades and transfer journal dependencies to the surviving dependency or a `freefrag`.

Truncation and block freeing are also staged. Non-SUJ full truncation uses `softdep_setup_freeblocks()` to snapshot block pointers into `freeblks/freework`, zero inode pointers, cancel obsolete allocations, write the zeroed inode, then process frees after the safe write. SUJ truncation uses `softdep_journal_freeblocks()` to journal top-level frees/truncation, update the inode block under protection, cancel dependencies beyond the truncation point, zero partial data, and then use `freework` plus `indir_trunc()` to release direct and indirect trees asynchronously.

Directory-add setup allocates a `diradd`, links it into a parent `pagedep`, ties it to the target inode's `inodedep` or SUJ `jaddref`, and handles new directory creation with `mkdir` and `newdirblk` dependencies so `.` and `..` reach stable storage before the parent entry becomes durable. A new directory block may force the caller to sync when the directory was extended through an indirect block.

## State and Data Flow

- Global state includes `dep_current[]`, `dep_highuse[]`, `dep_total[]`, `dep_write[]`, `softdepmounts`, `max_softdeps`, `softdep_callout`, cleanup request flags, and many debug/stat sysctls under `debug.softdep`.
- Per-mount state lives in `struct mount_softdeps` via `ump->um_softdep`: per-filesystem rw lock, pending work and journal lists, hash tables for `pagedep`, `inodedep`, `newblk`, `bmsafemap`, and freed indirect blocks, all-dependency tracking lists, journal block allocator state, cleanup counters, dirty cylinder groups, unlinked inodes, and mkdir tracking.
- `worklist` is the common embedded header for all dependency objects. `wk_type`, `wk_state`, `wk_mp`, list links, and optional invariant source location drive type-specific dispatch and lifetime checks.
- Important dependency families visible here are `pagedep`, `inodedep`, `bmsafemap`, `newblk`, `allocdirect`, `indirdep`, `allocindir`, `freefrag`, `freeblks`, `freework`, `freefile`, `diradd`, `mkdir`, `newdirblk`, `jaddref`, `jremref`, `jmvref`, `jnewblk`, `jfreeblk`, `jfreefrag`, `jtrunc`, `jfsync`, `jseg`, `jsegdep`, and `freedep`.
- State flags such as `ATTACHED`, `DEPCOMPLETE`, `COMPLETE`, `ALLCOMPLETE`, `INPROGRESS`, `IOSTARTED`, `ONWORKLIST`, `ONDEPLIST`, `GOINGAWAY`, `UNDONE`, `NEWBLOCK`, `MKDIR_BODY`, `MKDIR_PARENT`, `EXTDATA`, `UNLINKED`, `DELAYEDFREE`, and `UFS1FMT` encode whether an object is still attached to on-disk state, pending I/O, journaled, canceled, or safe to free.
- Journal-space state is maintained by `jblocks`: extents in the hidden `.sujournal` file, free/low/min thresholds, segment sequence numbers, oldest valid segment tracking, pending/active segment queues, and suspension flags.
- Block allocation state flows from cylinder group bitmap update to `newblk`, from `newblk` to `allocdirect` or `allocindir`, into inode or indirect dependency lists, then to `bmsafemap` completion and finally to `free_newblk()` once the relevant pointer and journal ordering requirements are met.
- Truncation state flows from inode block pointer snapshots into `freeblks`, then into top-level and nested `freework` items. `fw_ref`, `fw_parent`, `fw_indir`, `fw_off`, `fw_start`, and `fb_jblkdephd/fb_jwork/fb_freeworkhd` coordinate asynchronous indirect-tree traversal and delayed bitmap frees.
- Directory-add state flows through `diradd`, `pagedep`, `inodedep`, and optionally SUJ `jaddref` records. New directories add `mkdir` and `newdirblk` dependencies, with `inodedep->id_mkdiradd` preserving rename-related `.`/`..` dependencies.

## Dependencies

This code is tightly coupled to FreeBSD kernel subsystems: vnode and mount locking, buf/bio APIs, GEOM provider I/O and BIO flush, kthreads, callouts, sysctls, AST registration, VM pager truncation, UFS inode and block mapping helpers, quota accounting, snapshot handling, and FFS block allocation/free/update routines.

Header dependencies in this chunk include core kernel headers, UFS/FFS headers (`dir.h`, `inode.h`, `ufsmount.h`, `fs.h`, `softdep.h`, `ffs_extern.h`, `ufs_extern.h`), VM headers, and GEOM headers. Runtime calls include `bread()`, `ffs_breadz()`, `bdwrite()`, `bwrite()`, `bawrite()`, `getblk()`, `geteblk()`, `VOP_FSYNC()`, `ffs_update()`, `ffs_syncvnode()`, `ffs_blkfree()`, `UFS_BALLOC()`, `ufs_bmaparray()`, `ffs_vgetf()`, `VFS_SYNC()`, `vfs_write_resume()`, `vn_start_secondary_write()`, `vnode_pager_setsize()`, `vn_pages_remove()`, quota helpers, and GEOM `g_io_request()`.

Many declared helpers are not defined in this chunk and are resolved later in the file, including inode/block write initiation and completion handlers, buffer rollback/rollforward logic, pagedep removal/merge helpers, cleanup scheduling, `softdep_sync_metadata()`, `softdep_sync_buf()`, `softdep_request_cleanup()`, and remaining directory remove/change handling.

## Risks and Edge Cases

- Correctness depends on strict lock ordering across vnode locks, buffer locks, the per-filesystem softdep lock, mount locks, UFS locks, and the global softdep mutex. Several paths intentionally drop and reacquire locks and return `ERELOOKUP` because the caller must restart after state may have changed.
- Journal-space flow control is delicate. If `softdep_prealloc()` or link/rename prechecks are bypassed or underestimated, `softdep_process_journal()` can hit an out-of-journal-space path and rely on waiting, sync, or filesystem suspension for recovery.
- The worklist ordering invariant matters: block and fragment frees must complete before inode free/reuse can generate identical `<vfsid, inode, lbn>` identities. Queue manipulation bugs can produce stale dependency reuse or premature bitmap exposure.
- Segment completion and journal reclamation require both ordered segment write completion and optional cache flush completion. Releasing `jsegdep` too early can let journal records be overwritten before dependent metadata is stable.
- Bitmap safety depends on `bmsafemap` completion: allocation pointers must not hit disk before inode/block allocation bitmaps, and freed bitmaps must not hit disk before old pointers are cleared.
- Truncation is high risk because it mutates inode pointers, indirect buffers, page cache state, quota/block counts, journal records, and dirty buffer dependencies. Partial indirect truncation uses saved buffers and serialized `ir_trunc` queues, with restart behavior when `cancel_pagedep()` must wait for journal entries.
- Several paths panic on invariant violations rather than returning errors, which is typical for kernel consistency failures but means metadata dependency corruption is fail-stop.
- UFS1/UFS2 pointer format handling is manual in indirect code and inode-block update code; incorrect format flags would corrupt saved indirect copies or on-disk inode images.
- Existing dirty-worktree state was not modified except for this chunk report; no final per-file report was generated.

## Cross-Chunk References

- The chunk starts with the complete disabled-softdep stubs, but active behavior continues far beyond this chunk. The merge report must combine this with later chunks for the full softdep API behavior.
- Prototypes for many later functions appear in lines 699-931 but their bodies are outside this chunk, including I/O initiation/completion, pagedep flushing/freeing, inode block rollback/rollforward, bmsafemap write handling, cleanup, remove/change directory operations, and exported sync/request helpers.
- `softdep_change_directoryentry_offset()` begins at line 8875 and is incomplete at line 8878; its implementation and the rest of directory-entry movement/removal/rename dependency handling are in the next chunk.
- `softdep_setup_directory_add()` calls `diradd_lookup()`, `diradd_inode_written()`, `merge_diradd()`, and later completion/free helpers whose definitions are outside this visible range.
- Truncation and free paths in this chunk call later-defined `cancel_indirdep()`, `free_indirdep()`, `handle_jwork()`, `handle_workitem_freefile()`, `handle_workitem_remove()`, and cleanup request functions.
- Journal completion in this chunk hands off to later bmsafemap, inode, and buffer write completion code through `handle_written_bmsafemap()`, `handle_written_inodeblock()`, `handle_allocdirect_partdone()`, `handle_allocindir_partdone()`, and rollback/rollforward helpers.

### Chunk 2: lines 8879-15020

# Chunk Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_softdep.c lines 8879-15020

## Scope

This chunk covers the middle and later soft-updates implementation for FreeBSD FFS/UFS. It begins inside `softdep_change_directoryentry_offset()` and covers directory add/remove/change dependency cancellation, SUJ journal reference handling, unlinked-inode list maintenance, disk-write initiation/completion rollbacks, inode/cylinder-group sync paths, dependency-pressure cleanup, suspend checks, and DDB debugging helpers.

## APIs and Entry Points

- `softdep_setup_remove()` creates `dirrem` work for directory-entry removal.
- `softdep_setup_directory_change()` combines removal of an old reference with addition of a new reference for rename/change.
- `softdep_change_linkcnt()` records inode link-count deltas.
- `softdep_setup_sbupdate()` tracks SUJ unlinked-inode head updates in superblock writes.
- `softdep_disk_io_initiation()` and `softdep_disk_write_complete()` are the central pre/post write dependency hooks.
- `softdep_load_inodeblock()` and `softdep_update_inodeblock()` preserve effective link counts and transfer inode deps to inode-block buffers.
- `softdep_fsync()`, `softdep_sync_metadata()`, and `softdep_sync_buf()` drain dependencies for sync/fsync.
- `softdep_slowdown()`, `softdep_request_cleanup()`, `softdep_check_suspend()`, and `softdep_get_depcounts()` support cleanup, throttling, and suspend coordination.
- DDB commands expose softdep state for `inodedep`, `worklist`, `mkdir`, `allocdirect`, and `allocindir`.

## Control Flow

Directory removals flow through `newdirrem()`, which allocates `dirrem`, optional SUJ `jremref`s, finds the relevant `pagedep`, and checks for a colliding `diradd`. If the add was never visible on disk, `cancel_diradd()` cancels add-side journal refs, transfers journal work, marks the remove complete, and frees the obsolete add.

Directory changes build on that path. `softdep_setup_directory_change()` allocates a replacement `diradd`, calls `newdirrem()` for the old inode, then attaches the add to the new inode’s dependency lists. SUJ paths bind the latest `jaddref`; non-SUJ paths wait on inode write completion or move directly to pending if already stable. Directory rename/reparenting uses `merge_diradd()`, `cancel_mkdir_dotdot()`, and `cancel_diradd_dotdot()` to keep `.`/`..` ownership coherent.

The disk write path uses rollback-before-write and roll-forward-after-write. Directory pages temporarily hide uncommitted entries; inode blocks hide unwritten allocations and roll back pointers/sizes/link counts; indirect blocks swap to safe copies; cylinder-group bitmaps hide allocations whose journal records are not stable. Completion restores memory, releases only successful dependencies, and reattaches items needing another write.

Sync and cleanup repeatedly force prerequisites forward: journal refs, bitmap writes, inode writes, parent directory writes, dirty vnode flushes, worklist processing, and delayed vnode inactivation.

## State and Data Flow

- `diradd`: new directory references, offsets, target inode, prior `dirrem` for `DIRCHG`, and delayed journal work.
- `dirrem`: removed directory refs, old inode, parent dir inode, journal remove refs, and delayed work.
- `mkdir`: tracks `MKDIR_PARENT` and `MKDIR_BODY` completion for `.` and `..`.
- `inodedep`: link deltas, unlinked-list state, block pointer updates, journal inode refs, `id_bufwait`, `id_inowait`, and bitmap dependency coupling.
- `pagedep`: directory-page add/remove/move dependencies and `NEWBLOCK` state.
- `indirdep`: safe copies, truncation state, and staged `allocindir` lists.
- `bmsafemap`: cylinder-group bitmap deps for inode/block allocation and free work.
- `sbdep`: superblock dependency for SUJ `fs_sujfree` and checksum recomputation.

## Dependencies

This chunk depends on softdep workitem macros/types, journal helpers, dependency lookup helpers, allocation/free helpers, UFS/FFS geometry and bitmap routines, vnode/buffer APIs, mount/device state, AST/callout/sleep primitives, and per-filesystem/global softdep locks.

## Risks and Edge Cases

- Live buffers are temporarily mutated before write; missed roll-forward paths would corrupt cache state.
- Lock dropping around waits, vnode locks, allocation, and I/O requires repeated revalidation.
- Failed writes roll memory forward but do not release dependency ordering.
- SUJ unlinked-inode list ordering is delicate; `fs_sujfree`, `di_freelink`, and `UNLINK*` flags must be written in order.
- Rename/reparenting has subtle `.`/`..` ownership transfers and panic checks.
- UFS1/UFS2 inode rollback logic is duplicated and must stay behaviorally aligned.
- Suspend cleanup includes a forced-unmount workaround for orphaned `indirdep` objects after disk failure.
- Cleanup avoids snapshot/COW and locked-inode recursion paths to prevent deadlock or incoherent snapshots.

## Cross-Chunk References

- Earlier chunks define data structures, flags, workitem macros, counters, lock macros, journal helpers, and constructors.
- Earlier directory-add paths create `diradd`, `mkdir`, `jaddref`, `newdirblk`, `pagedep`, `inodedep`, `newblk`, and `bmsafemap` state completed here.
- Earlier block allocation/truncation code defines `allocdirect`, `allocindir`, `freeblks`, `freework`, `freefrag`, `freedep`, `jblkdep`, and related cancellation/free helpers.
- This range reaches the end of the `SOFTUPDATES` implementation; the final per-file report should merge it with chunk 1 rather than treating it as standalone.
