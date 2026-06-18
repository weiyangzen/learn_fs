# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/udfs/udf_dir.c

## Purpose

Implements UDFS directory operations: lookup, create, link, mkdir, rename, unlink, rmdir, empty-directory checks, parent-chain checks, directory-entry insertion, FID rewriting, and `..` repair. It bridges Solaris vnode directory semantics to UDF File Identifier Descriptors with compressed UDF names and descriptor tags.

## Main Entry Points

- `ud_dirlook()`: looks up a name in a directory, using DNLC when allowed and scanning FIDs otherwise.
- `ud_direnter()`: common create/link/mkdir/rename entry point.
- `ud_dirremove()`: common unlink/rmdir/remove-for-rename path.
- `ud_dircheckforname()`: scans a directory for an existing name and optionally records a reusable deleted slot.
- `ud_dirempty()`: verifies a directory contains only deleted entries and the parent entry.
- `ud_dircheckpath()`: walks parent FIDs to prevent moving a directory under its descendant.
- `ud_dirmakeinode()`, `ud_dirmakedirect()`, `ud_diraddentry()`: allocate new inode/directory content and install an FID.
- `ud_dirrename()`, `ud_dirfixdotdot()`: replace an existing target and update child parent FID/link counts.
- `ud_dirprepareentry()`, `ud_write_fid()`: grow/reuse directory space and write tagged FIDs, including block-crossing entries.

## Control Flow And State

Lookups verify directory execute access, treat empty name and `.` specially, use `i_diroff` as a rotating search start, and scan UDF FIDs through `ud_get_next_fid()`. Parent entries use `FID_PARENT` and are exposed as `..`; ordinary names are converted with `ud_uncompress()`. Lookup of `..` drops and reacquires the directory read lock around `ud_iget()` and rechecks mtime/location to avoid returning stale parent results after concurrent rename.

`ud_direnter()` validates names, forbids creating or renaming over `.`/`..`, pre-increments source link count for link/rename durability, verifies search/write access, checks rename ancestry under `udf_rename_lck`, searches for an existing target, and then either dispatches to `ud_dirrename()` or creates and inserts a new entry. On create/mkdir insertion failure it clears the new inode link count and releases it.

`ud_dirremove()` checks sticky-directory permissions, mount-point/busy state for directories, rmdir invariants, and directory emptiness. The last directory entry is removed by truncating the directory; other entries are marked `FID_DELETED`, retagged, and written back. Link counts, DNLC entries, inode times, and vnode events are updated after the on-disk directory operation.

Directory creation writes only a `FID_PARENT` entry, not a `.` entry; the code relies on UDFS semantics where directories have one link from their parent. `ud_dirprepareentry()` either reuses a deleted slot or extends the directory with `ud_bmap_write()`. If extension converts an embedded directory to allocation descriptors, existing FID tags are recalculated because tag locations change.

## Dependencies

Depends on UDFS FID layout/macros, Unicode compression helpers, `ud_get_next_fid()`, `ud_make_tag()`, inode allocation/update/truncation, `ud_iaccess()`, `ud_sticky_remove_access()`, DNLC, vnode event hooks, and Solaris vnode/fbuf locking conventions.

## Risks

Correctness depends on lock ordering across `i_rwlock`, `i_contents`, vnode vfs locks, and the filesystem rename mutex. Rename/link paths pre-adjust link counts and rely on later rollback on error. Directory entries can cross logical-block boundaries, so partial FID writes must keep tags and buffers consistent. The file returns historical Solaris errors in some cases (`EEXIST` for not-empty-style failures, `ESAME` for self-rename), which callers must understand.
