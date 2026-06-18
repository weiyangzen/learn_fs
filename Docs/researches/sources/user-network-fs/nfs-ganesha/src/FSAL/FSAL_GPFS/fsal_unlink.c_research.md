# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_unlink.c

- **Purpose:** Implements removal of a named filesystem object from a GPFS directory handle.
- **Important APIs/types/functions:** `GPFSFSAL_unlink`, `fsal_internal_stat_name`, `fsal_internal_unlink`, `gpfsfsal_xstat_t`, and `struct gpfs_fsal_obj_handle`.
- **Control flow:** The wrapper unwraps the parent directory private handle, stats the target name under the export fd to validate and collect metadata, then calls `fsal_internal_unlink` with the parent handle, name, and stat buffer. Errors from either step are returned directly.
- **State and persistence behavior:** Persistent namespace deletion occurs in GPFS through `OPENHANDLE_UNLINK_BY_NAME` in the internal helper under caller credentials. The wrapper keeps no state and does not explicitly invalidate caches.
- **Dependencies and integration points:** Called by `handle.c` `file_unlink` as the object op implementation. Depends on `op_ctx`, export fd, GPFS private handles, and internal stat/unlink helpers.
- **Risks:** The pre-stat and unlink are race-prone if the name changes between operations. The same path handles file and directory removal according to GPFS/openhandle semantics, so caller expectations for unlink vs rmdir must match the lower layer. Cache consistency depends on GPFS upcalls or higher layers.
- **Test signals:** Cover file unlink, directory removal if supported by the opcode, missing target, permission errors under caller credentials, target replaced between stat and unlink, and post-unlink cache/upcall behavior.
