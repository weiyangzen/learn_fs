# sources/storage-engines/wiredtiger/src/meta/meta_table.c

## Purpose
Implements the common metadata table access layer, including cached metadata cursors and special routing for bootstrap keys stored in the turtle file.

## Important APIs, Types, and Functions
Key functions are `__wt_metadata_cursor_open`, `__wt_metadata_cursor`, `__wt_metadata_cursor_release`, `__wt_metadata_cursor_close`, `__wt_metadata_insert`, `__wt_metadata_update`, `__wt_metadata_remove`, `__wt_metadata_search`, `__wt_metadata_turtle_rewrite`, `__wt_metadata_btree_id_to_uri`, and `__wt_verbose_dump_metadata`. `__metadata_turtle` identifies keys handled by the turtle file: metadata file URI, version, compatibility, version string, and live-restore state.

## Control Flow
Cursor open uses `__wt_open_cursor` on `file:WiredTiger.wt` without an active dhandle and skews metadata eviction priority. `__wt_metadata_cursor` reuses a per-session cached cursor unless it is already marked in use, in which case it opens a temporary cursor. Insert rejects turtle keys. Update routes turtle keys through live-restore turtle update or locked turtle update, otherwise records meta tracking when active and performs overwrite insert. Remove first searches and releases the cursor so meta tracking can use the cached cursor, then removes the key. Search routes turtle keys to turtle readers and reads normal metadata at read-uncommitted isolation.

## State and Persistence Behavior
Normal metadata writes persist schema, file, checkpoint, and system entries in the metadata btree. Turtle-key updates rewrite the text turtle file. Session state includes `session->meta_cursor` and `WT_CURSTD_META_INUSE`; cursor release either resets the cached cursor or closes temporary cursors. Metadata reads intentionally use read-uncommitted isolation because schema/metadata locks, not normal transactions, serialize metadata updates.

## Dependencies and Integration Points
The file depends on cursor APIs, metadata/turtle locks, live-restore turtle hooks, meta tracking, eviction priority, config strings, and diagnostic message output. It is the central dependency for schema, checkpoint, recovery, extension, and diagnostic metadata operations.

## Risks and Edge Cases
Turtle keys cannot be inserted or removed through normal metadata operations. Cursor caching requires correct in-use flag handling to avoid nested metadata operations clobbering the cursor. Read-uncommitted metadata access is intentional but means correctness relies on external locks. Remove performs a pre-search so that rollback can restore prior values. `__wt_metadata_btree_id_to_uri` scans all metadata and tolerates entries without `id`.

## Test Signals
Schema create/drop/rename tests, metadata cursor nesting, turtle update/read paths, live-restore turtle operations, metadata rollback, and verbose metadata dumping all exercise this layer. Eviction behavior should keep the metadata btree highly resident under cache pressure.
