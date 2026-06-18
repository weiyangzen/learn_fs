# sources/storage-engines/wiredtiger/src/include/truncate.h

Purpose: `truncate.h` defines the compact context object used to carry state through a range truncate operation.

Important APIs and types: `WT_TRUNCATE_INFO` stores the owning session, URI, optional start and stop cursors, original start and stop keys, and flags `WT_TRUNC_EXPLICIT_START` and `WT_TRUNC_EXPLICIT_STOP` that distinguish caller-provided boundaries from inferred range boundaries.

Control flow and state: truncate code fills this structure before validating cursors and applying row-store or column-store range deletion. The flags guide boundary handling, error reporting, and whether original keys need to be retained while cursors move during truncate processing.

Persistence behavior: the structure itself is transient. Persistent effects are produced elsewhere as tombstone updates, page-delete records, transaction operations, and metadata/stat changes when the truncate is committed or rolled back.

Dependencies and integration points: depends on `WT_SESSION_IMPL`, public `WT_CURSOR`, `WT_ITEM`, and transaction/truncate implementation code. It connects public `WT_SESSION::truncate` inputs to lower-level cursor, btree, transaction, and reconciliation code.

Risks: lifetime of `orig_start_key` and `orig_stop_key` must outlive the truncate operation. Mis-set explicit-bound flags can delete too broad or too narrow a range. Cursor movement during truncate makes key preservation important for diagnostics and transaction operation reconstruction.

Test signals: truncate with no bounds, start-only, stop-only, and both bounds; row and column stores; rollback and prepared transactions; empty ranges; cursor repositioning; and crash/recovery tests that verify committed truncates persist while rolled-back truncates do not.
