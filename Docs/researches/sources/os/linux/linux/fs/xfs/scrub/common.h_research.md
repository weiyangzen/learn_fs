# File Research: sources/os/linux/linux/fs/xfs/scrub/common.h

## Role
Declares shared scrub helper APIs and inline predicates used across the XFS scrub and repair subsystem.

## Main Interface Groups
- Transaction helpers: `xchk_trans_alloc`, `xchk_trans_alloc_empty`, `xchk_trans_cancel`.
- Error processors: AG/block, realtime block, file-block, and xref variants.
- Outcome setters: corrupt, xref corrupt, preen, warning, incomplete, and quota-check corruption.
- Setup functions for AG headers, filesystems, inode forks, directories, xattrs, symlinks, parent pointers, dirtree, quotas, fscounters, nlinks, and realtime metadata.
- AG and rtgroup lifecycle helpers, btree cursor initialization/freeing, and rmap owner counting.
- Inode helpers for safe iget, handle/live inode installation, inode lock tracking, and block counting.

## Important Inline Logic
- `xchk_ag_init_existing` and `xchk_rtgroup_init_existing` convert missing allocation/realtime groups referenced by metadata into corruption.
- `xchk_iget_safe` wraps iget in an empty transaction to avoid deadlocks on malformed inobt structures during setup.
- `xchk_skip_xref` suppresses xrefs once primary or xref corruption is already known.
- `xchk_needs_repair` treats corrupt, xcorrupt, and preen as repair-worthy.
- `xchk_could_repair` checks user repair intent and avoids nested post-repair setup.
- `xchk_need_intent_drain` records when expensive drain gates are needed.

## Conditional Compilation
Provides no-op or `-EFSCORRUPTED` stubs for realtime helpers without `CONFIG_XFS_RT`, and quota setup stubs without `CONFIG_XFS_QUOTA`.

## Notes
This header is a central contract for scrub setup and flag behavior; changes here affect most scrubbers.
