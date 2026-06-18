# sources/storage-engines/wiredtiger/test/model/src/core/verify.cpp

Purpose: compares a WiredTiger table against the in-memory model table, optionally at a checkpoint.

Important APIs and functions: `kv_table_verify_cursor::has_next` skips deleted model items. `verify_next` advances the model cursor and compares the expected key/value, allowing any value visible at the same timestamp/checkpoint via `contains_any`. `get_prev` supports diagnostic messages. `kv_table_verifier::verify` opens a WiredTiger session and table cursor, optionally with `checkpoint=<name>`, iterates all WT records, compares to the model, checks for extra model records, and finally calls `session->verify(..., "strict")`, ignoring `EBUSY` with a warning.

Control flow and state: verification cursor is explicitly not thread-safe and holds an iterator into the model table map. RAII guards close session/cursor. Verbose diagnostic paths exist but `_verbose` is false by default.

Dependencies and integration: used by `kv_table::verify` and model tests/tools. Depends on data conversion helpers and WiredTiger cursor/session APIs.

Risks and test signals: key ordering must match `data_value` ordering and WiredTiger cursor order for supported formats. Strict verify may be skipped on `EBUSY`, leaving content comparison as primary signal. Mismatches throw `verify_exception` with the observed and previous model pair.
