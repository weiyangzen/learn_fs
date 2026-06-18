# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_rename.c

- **Purpose:** Implements GPFS rename/move of a named object between directory handles.
- **Important APIs/types/functions:** `GPFSFSAL_rename`, `fsal_internal_stat_name`, `fsal_internal_rename_fh`, `struct gpfs_fsal_obj_handle`, and `struct gpfs_fsal_export`.
- **Control flow:** Converts old and new public directory handles to GPFS private handles, stats the old name in the old directory to validate existence and collect metadata, then calls `fsal_internal_rename_fh` with old and new directory handles plus names. Any FSAL error from stat or rename is returned directly.
- **State and persistence behavior:** The persistent namespace mutation is performed by GPFS through `OPENHANDLE_RENAME_BY_FH` in the internal helper. This wrapper stores no state and does not update cached attributes directly.
- **Dependencies and integration points:** Called by `handle.c` `renamefile`, then by Ganesha object operation dispatch. Depends on current export fd from `op_ctx`, private GPFS object handles, internal stat/rename helpers, and FSAL error conversion.
- **Risks:** The pre-stat introduces an existence/type check but does not eliminate rename races. Parent pre/post attribute outputs are ignored in the caller path. Cache invalidation is not explicit here and depends on upper layers or GPFS upcalls.
- **Test signals:** Cover same-directory rename, cross-directory rename, missing source, existing destination replacement semantics, permission failures under caller credentials in `fsal_internal_rename_fh`, and cache/upcall visibility after rename.
