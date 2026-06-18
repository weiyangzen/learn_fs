# sources/sync-backup/casync/src/rm-rf.c

Purpose: recursively removes files/directories with guard rails for physical mount boundaries and immutable inode flags.

Important APIs/types/functions: `rm_rf_children`, `rm_rf_at`, `rm_rf`, plus `unlinkat_immutable`. `RemoveFlags` control root removal, recursive descent, physical filesystem restriction, and whether immutable attributes may be cleared.

Control flow/state: `rm_rf_at` opens/lstats the root and optionally unlinks it. `rm_rf_children` iterates directory entries, skips virtual filesystems when requested, descends into directories with `xopendirat`, and removes entries with `unlinkat_immutable`. Immutable handling can clear flags before unlinking.

Dependencies/integration: uses Linux statfs magic constants, `chattr.h`, openat/unlinkat patterns, and util directory helpers. Used by tests and cleanup paths for stores/trees.

Risks/test signals: destructive by design; flag interpretation is critical. Mount-boundary detection depends on `statfs` and root device state. `test-casync.c` uses `rm_rf` for cleanup, but no exhaustive deletion safety test appears here.

Source research group: `subset-b-009122`.
