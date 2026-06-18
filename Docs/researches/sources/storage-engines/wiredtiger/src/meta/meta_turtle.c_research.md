# sources/storage-engines/wiredtiger/src/meta/meta_turtle.c

## Purpose
Bootstraps and maintains the turtle file, the small text file that points to the metadata btree and stores startup-critical metadata such as version, compatibility, and live-restore state. It also loads metadata from hot-backup files and handles partial-backup restore setup.

## Important APIs, Types, and Functions
Primary APIs include `__wt_turtle_exists`, `__wt_turtle_init`, `__wt_turtle_validate_version`, `__wt_turtle_read`, `__wt_turtle_update`, and `__wt_read_metadata_file`. Private helpers create default metadata config, create the metadata file, load `WiredTiger.backup`, rebuild missing bulk-load stubs, manage partial backup target URI hashes, and process metadata backup entries.

## Control Flow
Startup removes leftover turtle set files when allowed, checks for `WiredTiger.backup` and `WiredTiger.turtle`, and either validates the existing turtle or rebuilds metadata from backup. When loading backup metadata, it reads key/value line pairs, updates metadata, and for partial restores records non-target tables so schema drop can clean linked entries and collect btree IDs for history-store truncation. If metadata is newly loaded or the turtle was unreadable under salvage, it writes a new turtle file with default metadata config.

## State and Persistence Behavior
The turtle file is rewritten by creating `WiredTiger.turtle.set`, writing compatibility/live-restore/version/key/value pairs, syncing, and renaming into place. `__wt_turtle_read` returns default metadata config when the turtle file is absent during initial metadata creation. Hot backup loading sets connection flags such as `WT_CONN_WAS_BACKUP` and partial-restore state. Version validation stores `conn->recovery_version`.

## Dependencies and Integration Points
This file depends on the stream layer, filesystem exists/remove/rename helpers, schema create/drop, metadata table updates, config parsing, live restore turtle hooks, backup target hashes, block manager bulk file creation, version compatibility helpers, and the turtle lock.

## Risks and Edge Cases
Windows rename behavior can leave only the turtle set file; `__wt_turtle_exists` repairs that by renaming it into place. Turtle read failures normally panic with `WT_TRY_SALVAGE`, except optional compatibility/live-restore keys or salvage mode. Restore from backup is incompatible with metadata verification. Partial backup restore only accepts `table:` targets and must load all metadata first so schema drop can clean secondary references. Turtle updates are fatal on failure because startup metadata may be corrupt.

## Test Signals
Startup/reopen tests, salvage with corrupted turtle files, backup restore, partial backup restore, live restore, compatibility-version checks, bulk-load backup restore, and failpoint-style abort before turtle update are the key signals.
