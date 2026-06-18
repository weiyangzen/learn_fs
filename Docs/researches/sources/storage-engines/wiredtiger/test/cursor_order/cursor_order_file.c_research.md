# sources/storage-engines/wiredtiger/test/cursor_order/cursor_order_file.c

## Purpose
This file provides table/file creation, initial bulk loading, and verification helpers for the cursor-order test.

## Important APIs, Types, and Functions
- `file_create` creates a WiredTiger file with row or record-number key format, tuned page sizes, and `split_deepen_min_child=200`.
- `load` creates the file, opens a bulk cursor, inserts `cfg->nkeys` ordered records, sets `cfg->key_range`, closes the cursor, checkpoints, and closes the session.
- `verify` opens a session and calls `testutil_verify`.

## Control Flow
`load` calls `file_create`, opens a bulk cursor, iterates keys from 1 through `nkeys`, formats row keys as zero-padded strings or column keys as recnos, stores a formatted `WT_ITEM` value, inserts, checkpoints, and returns. `verify` is a simple wrapper around WiredTiger verification.

## State and Persistence Behavior
The loaded file is persistent and checkpointed before workload threads run. `cfg->key_range` records the highest loaded key so append workloads know where to continue.

## Dependencies and Integration Points
The file depends on `SHARED_CONFIG`, active `WT_CONNECTION`, `WT_SESSION`, bulk cursor semantics, and `testutil_verify`. It is called by the cursor-order operations module and driver.

## Risks and Test Signals
Create tolerates `EEXIST`; other create, bulk insert, checkpoint, or verify errors fail. Bulk loading assumes ordered keys and correct key type for row versus variable-column mode.
