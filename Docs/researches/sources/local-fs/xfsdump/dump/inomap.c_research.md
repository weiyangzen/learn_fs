# File Research: sources/local-fs/xfsdump/dump/inomap.c

`inomap.c` builds and serializes the inode-selection map used by xfsdump. It decides which inodes participate in a dump, prunes unnecessary directory hierarchy, estimates data volume, and chooses stream startpoints for parallel dumps.

Main phases in `inomap_build`:
- Syncs the filesystem so bulkstat sees current inode state.
- Counts inode groups with `inogrp_iter`, initializes the in-memory map, and pre-populates a segment for each inode group so later subtree traversal can set states in any order.
- Phase 1 constructs the initial dump list. For full dumps it iterates all inodes with `bigstat_iter`; for subtree dumps it recursively descends requested paths with `diriter`.
- Phase 2 prunes unchanged support directories if they do not contain changed descendants, unless `skip_unchanged_dirs` already avoided support-directory inclusion.
- Phase 3 calculates non-directory stream startpoints from estimated dump sizes.

Map model:
- Uses `hnk_t` hunks containing `seg_t` segments. Each segment covers `INOPERSEG` inodes, with three bitmap planes (`lobits`, `mebits`, `hibits`) encoding one of eight `MAP_*` states.
- Keeps a parallel inode-to-generation map (`i2gseg_t`) for directory entry generation numbers.
- `seg_addr_t` contexts cache hunk/segment/inode offsets for faster repeated lookup and iteration.

Inode states:
- `MAP_INO_UNUSED`: no known inode.
- `MAP_DIR_NOCHNG` / `MAP_NDR_NOCHNG`: in use but not dumped.
- `MAP_DIR_CHANGE` / `MAP_NDR_CHANGE`: selected for dump.
- `MAP_DIR_SUPPRT`: unchanged directory still needed to reconstruct hierarchy.
- Reserved states 6 and 7 are unused.

Selection logic:
- `cb_add` compares inode mtime/ctime against incremental and resume base times.
- Resume ranges are treated specially so previously undumped portions can still be included.
- Regular non-directories may be excluded by max dump file size unless they are quota files.
- Files with `XFS_XFLAG_NODUMP` are excluded only when `allowexcludefiles_pr` is true.
- HSM hooks can estimate dump size or offsets for offline/dual-residency files.

Startpoint logic:
- `cb_spinit` divides total estimated non-directory bytes plus header overhead by stream count.
- `cb_startpt` uses heuristics (`TOO_SHY`, `TOO_BOLD`) to either keep a file in the current stream, begin the next stream at a file boundary, or split a very large file at a block-aligned offset.
- `quantity2offset` converts “real data bytes behind this point” into a file offset by reading extent maps.

Serialization:
- `inomap_writehdr` fills content inode header fields with hunk count, segment count, directory count, non-directory count, first/last inode, and estimated data size.
- `inomap_dump` writes each hunk through the drive layer after byte-order translation with `xlate_hnk`.

Potential issues:
- `inomap_build` passes a freshly allocated context from `inomap_alloc_context()` into phase 3 without freeing it afterward.
- The `else if (resumed)` branch in `cb_add` contains `assert(changed)` in a path reached only when the preceding `if (changed)` failed, which looks logically inconsistent or obsolete.
- Size estimates are intentionally rough for normal files and affect stream balancing and max-size pruning.
