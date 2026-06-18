# File Research: sources/os/linux/linux/fs/xfs/scrub/dir_repair.c

## Role
Repairs corrupt XFS directory contents by rebuilding directory entries in a temporary directory and atomically replacing the target directory's data fork. It supports two rebuild strategies: salvaging plausible entries from damaged directory data or regenerating entries from parent pointers.

## Main Data Structures
- `struct xrep_dirent`: queued add/remove action containing name cookie, target inode, name length, file type, and action.
- `struct xrep_dir`: repair state containing queued dirents/names, temp exchange info, reusable DA args, parent scan state, orphanage adoption context, observed subdir/dirent counts, and name buffers.

## Setup and Teardown
- `xrep_setup_directory` enables directory update hooks, ensures orphanage availability, creates a temporary directory, and stores `struct xrep_dir` in `sc->buf`.
- `xrep_dir_teardown` tears down parent scanning and destroys queued-name storage.

## Parent Discovery
- Tries self-reference, dcache, current `..`, and finally a filesystem scan via findparent helpers.
- If no reliable parent can be found, the repaired directory may be temporarily rooted at the filesystem root and later moved to the orphanage.

## Salvage Mode
- Used when parent pointers are unavailable.
- Shortform entries are read from the local fork; block/data format entries are recovered by reading directory data blocks.
- Names are trimmed at NUL or slash, `.` and `..` are ignored, target inode numbers must be plausible and allocated, metadata tree crossings are rejected, and file type is derived from the target inode.
- Stashed entries are periodically flushed into the temp directory to cap memory usage at `XREP_DIR_MAX_STASH_BYTES`.

## Parent-Pointer Mode
- Scans all files for parent pointer xattrs that reference the directory being repaired and turns them into replacement dirents.
- Scans directories for child dirents pointing at the repaired directory to infer `..`.
- Uses live directory hooks (`xrep_dir_live_update`) to capture concurrent relevant dirent additions/removals into the tempdir update queue while scanning.
- Aborts quickly if zapped attr forks or zapped directories prevent reliable scanning.

## Replaying and Rebuilding
- `xrep_dir_replay_update` replays queued creates/removes into the temp directory using normal directory operations and per-operation transactions.
- `xrep_dir_finalize_tempdir` ensures all queued updates are replayed before the final exchange, repeating if hooks queued more updates.
- `xrep_dir_swap` sets the tempdir `..`, handles local-format fast copyout when possible, promotes local forks to block mapping form if needed, resets link count, and calls `xrep_tempexch_contents`.
- `xrep_dir_rebuild_tree` coordinates tempdir IOLOCK, transaction allocation, final replay, data fork exchange, temp fork reset, and lock release.

## Link Counts and Orphanage
- `xrep_dir_set_nlink` recomputes the directory link count as subdirectories plus two, handles unlinked-list cases, and can remove a live directory from the unlinked list if salvaged entries make it reachable.
- `xrep_dir_move_to_orphanage` moves a parentless repaired directory to the orphanage if it remains linked and unmoved after locks are reacquired.

## Preconditions and Limits
- Requires rmapbt for reaping old blocks.
- Requires atomic exchange-range support to commit rebuilt directory contents.
- Notes a risk with aliased multi-fsblock directory buffers if crosslinked with other metadata.
