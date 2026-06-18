# sources/storage-engines/wiredtiger/src/cursor/cur_table.c

## Purpose
Implements table cursors for non-simple WiredTiger tables. A table cursor composes one cursor per column group and lazily opens index cursors when updates require index maintenance. Simple tables are optimized by returning the single underlying data-source cursor with the public URI adjusted.

## Important APIs, types, and functions
`__wt_curtable_open` is the public entry point. `APPLY_CG` applies cursor operations across column-group cursors. `__wt_apply_single_idx` and `__apply_idx` project table values into index keys and apply index cursor operations. Accessors include `__curtable_get_key`, `__curtable_get_value`, `__curtable_set_key`, and `__curtable_set_valuev`. Cursor operations include `next`, `next_random`, `prev`, `reset`, `search`, `search_near`, `insert`, `update`, `remove`, `reserve`, `largest_key`, `bound`, `close`, and `__wt_table_range_truncate`.

## Control flow
Open resolves the table and optional projection columns, rejects incomplete tables, returns the underlying cursor for simple tables, or allocates `WT_CURSOR_TABLE`. It reformats value format and projection plan for projected cursors, handles `next_random` by disabling unsupported methods, initializes the table cursor, opens column-group cursors immediately, and saves normalized config for later index opens. Reads apply operations across column groups; `search_near` and random next position the primary column group first and then search secondary groups by copied key/recno. Updates open indices lazily. Insert detects duplicate primary keys when indices exist so overwrite can become an update; update removes old immutable-safe index entries before writing new column-group values and reinserting index keys; remove deletes index entries before removing column groups.

## State, persistence, and dependencies
The table cursor owns arrays of column-group cursors, index cursors, temporary value-copy buffers, copied config, projection plan, and the acquired `WT_TABLE` reference. Persistent changes land in underlying column-group and index data sources. Dependencies include schema table/index/column-group metadata, projection planning/merge/slice helpers, range truncate, transaction context checks, cursor bounds helpers, JSON column initialization, and standard cursor initialization/closing.

## Integration points
This file is the bridge from logical table APIs to physical data-source cursors. It coordinates with schema table completeness, column groups, index definitions, dump/json cursor behavior, next-random btree cursors, and truncate/index maintenance.

## Risks and test signals
Risks include index inconsistency on partial failure, preserving primary key/recno across column groups, projection buffer aliasing when users pass pointers from prior `get_value`, bounds rollback across multiple column groups, and lazy index open failure after the table cursor is already live. Tests should cover simple versus multi-column-group tables, projections, indices including immutable indices, overwrite inserts, duplicate keys, remove/update/truncate index cleanup, reserve returning a searchable value, `next_random`, bounds propagation/failure restore, incomplete table errors, dump/json cursors, and close cleanup after partial index-open failure.
