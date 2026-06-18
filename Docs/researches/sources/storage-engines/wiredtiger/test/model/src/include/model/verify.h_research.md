# sources/storage-engines/wiredtiger/test/model/src/include/model/verify.h

Purpose: declares verification primitives that compare modeled table contents against WiredTiger table or checkpoint cursors.

Important APIs and types: `verify_exception`; `kv_table_verify_cursor` with `has_next`, `set_checkpoint`, `verify_next`, and `get_prev`; `kv_table_verifier` with `verify` and `verify_noexcept`.

Control flow: a table creates a verification cursor over its sorted map. Optional checkpoint must be set before iteration. `has_next` skips non-visible/tombstone model items; `verify_next` compares WT key/value pairs to expected model pairs and advances; `get_prev` supports diagnostics. `kv_table_verifier::verify` opens WT cursors and walks both sides.

State and persistence: verification cursor holds references to the table's map, an iterator, optional previous iterator, and optional checkpoint pointer. It does not persist data. `kv_table_verifier` stores a table reference and verbose flag.

Dependencies and integration: includes `data_value.h` and `wiredtiger.h`; uses `kv_table`, `kv_table_item`, and `kv_checkpoint` through declarations from included headers. Called by `kv_table::verify`, `verify_noexcept`, `verify_workload`, and `verify_using_debug_log`.

Risks: `verify_cursor` is documented as not thread-safe; the referenced table map must remain stable during verification. Checkpoint must be set at the beginning only. Diagnostic quality depends on `get_prev` and data value printing. WT cursor configuration must match table/checkpoint modes.

Test signals: positive tests compare model and WT after workloads; negative tests mutate the model and expect `verify_noexcept` false. Checkpoint verification should be tested separately from live table verification.
