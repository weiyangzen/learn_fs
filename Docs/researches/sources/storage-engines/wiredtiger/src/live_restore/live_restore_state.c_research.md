<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c -->
# sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c

## Purpose
Manages live-restore state discovery, validation, persistence, turtle-file lock ordering, external stats reporting, and guardrails for opening a database with or without live restore enabled.

## Important APIs, Types, and Functions
Public/internal entry points include `__wti_live_restore_migration_complete`, `__wt_live_restore_migration_in_progress`, `__wti_live_restore_init_state`, `__wti_live_restore_set_state`, `__wt_live_restore_get_state_string`, `__wt_live_restore_turtle_update`, `__wt_live_restore_turtle_rewrite`, `__wt_live_restore_turtle_read`, `__wti_live_restore_get_state`, `__wti_live_restore_validate_directories`, `__wt_live_restore_validate_non_lr_system`, and `__wt_live_restore_init_stats`. Private helpers convert state strings and read persisted state from turtle metadata.

## Control Flow
Startup validation lists source and destination directories, rejects invalid source/destination combinations, reads any persisted live-restore state from the destination turtle file, then initializes in-memory state from that value or defaults to `BACKGROUND_MIGRATION` without immediately creating turtle metadata. State changes validate monotonic transitions and call `__wt_live_restore_turtle_rewrite` so the live-restore metadata entry is persisted. Turtle read/update/rewrite wrappers acquire the live-restore state lock before the turtle lock. Non-live-restore startup reads the turtle state and rejects opening a database stuck in background migration or cleanup.

## State and Persistence Behavior
State is persisted as a string in turtle metadata under `WT_METADATA_LIVE_RESTORE`; `WT_LIVE_RESTORE_STATE_STRING_MAX` bounds parsing. The internal state sequence is `NONE`, `BACKGROUND_MIGRATION`, `CLEAN_UP`, and `COMPLETE`, while application stats collapse this to init, in-progress, or complete. A missing turtle state means no prior live restore state exists; live-restore startup treats that as a fresh background migration, but destination validation rejects existing WiredTiger files to avoid corrupting an initialized directory.

## Dependencies and Integration Points
Uses metadata/turtle APIs, filesystem directory listing, connection flags, stats, stop-file suffix definitions, backup-file naming, and private live-restore structures. It is called from live-restore FS initialization, server cleanup, metadata/turtle wrappers in `meta_table.c` and `meta_turtle.c`, connection open validation, and stat initialization after the stat server starts.

## Risks and Edge Cases
There is a narrow early-crash window where live restore has in-memory state but no turtle state; restart will reject destination WiredTiger files and require user cleanup. Source validation requires a backup file and rejects source stop files so a destination directory is not accidentally used as a source. Complete-state validation rejects lingering stop files. The state lock must always be acquired before turtle lock to avoid deadlocks. String parsing is intentionally fixed-width and asserts the max length constant.

## Test Signals
Python and cppsuite live-restore tests should cover fresh startup, restart during background migration, restart during cleanup, complete-state reopening, non-live-restore open rejection while in progress, invalid source/destination directories, and stats values. Unit/API tests can also observe turtle wrapper behavior indirectly through persisted state and cleanup.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/live_restore/live_restore_state.c -->
