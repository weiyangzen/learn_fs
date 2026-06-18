# sources/sync-backup/casync/src/rm-rf.h

Purpose: declares recursive removal helpers and their flag contract.

Important APIs/types/functions: `RemoveFlags` includes `REMOVE_ROOT`, `REMOVE_RECURSIVE`, `REMOVE_PHYSICAL`, and `REMOVE_CHMOD`. Public functions are `rm_rf_children`, `rm_rf`, and `rm_rf_at`.

Control flow/state: no header state; flags define whether to remove just children or the root and whether cross-filesystem or immutable-flag behavior is allowed.

Dependencies/integration: includes `struct stat` because `rm_rf_children` can receive root device metadata for mount-boundary decisions.

Risks/test signals: callers must choose flags carefully. Passing `REMOVE_ROOT|REMOVE_PHYSICAL` to test cleanup is expected, but production deletion code should avoid overly broad roots.

Source research group: `subset-b-009122`.
