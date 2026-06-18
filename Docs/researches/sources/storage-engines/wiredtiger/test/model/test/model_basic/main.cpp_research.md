# sources/storage-engines/wiredtiger/test/model/test/model_basic/main.cpp

## Purpose
This is the foundational unit/integration test executable for the WiredTiger model layer. It validates `model::data_value`, basic key/value history behavior, row-store and column-store table verification against live WiredTiger, logged-table semantics, range truncation, oldest/stable timestamp rules, and debug-log replay verification.

## Important APIs, Types, and Functions
The file uses `model::kv_database`, `model::kv_table_ptr`, `model::kv_table_config`, `model::data_value`, `model::NONE`, and helpers from `model/test/wiredtiger_util.h`. The main scenarios are `test_data_value`, `test_model_basic`, `test_model_basic_wt`, `test_model_basic_column_wt`, `test_model_basic_logged`, `test_model_basic_logged_wt`, `test_model_truncate`, `test_model_truncate_wt`, `test_model_truncate_column_wt`, `test_model_oldest`, `test_model_oldest_wt`, and `test_model_debug_log_verify_wt`. WiredTiger-facing paths use `WT_CONNECTION`, `WT_SESSION`, `session->create`, and wrappers such as `wt_model_insert_both`, `wt_model_assert`, `wt_model_truncate_both`, `wt_model_set_oldest_timestamp_both`, and `verify_using_debug_log`.

## Control Flow
`main` parses shared test options, creates a temporary home directory, runs each scenario inside a `try` block, then removes the home unless `-p` was requested. Model-only tests directly mutate `kv_database` tables and assert expected snapshots. WiredTiger tests create a real table under a per-scenario subdirectory, perform paired model/WT operations, verify equality through `table->verify_noexcept(conn)`, deliberately perturb the model to prove verification can fail, and finally verify reconstruction through the debug log.

## State, Persistence, and Integration
The test uses a single `ENV_CONFIG` with table debug logging, retained logs, checkpoint retention, statistics, and small cache settings. State coverage includes timestamped update chains, non-timestamped globally visible updates, duplicate-key behavior with overwrite disabled, tombstones, column-store recnos, logged tables where timestamps are ignored, oldest timestamp monotonicity and restart behavior, and named debug-log verification for packed numeric keys. It integrates with the WiredTiger C API, common test utilities, model utility helpers, and debug-log parser support.

## Risks and Test Signals
This file is sensitive to semantic drift between the model and WiredTiger around timestamp visibility, logged table handling, range truncation boundaries, and persisted oldest timestamps. The strongest signals are direct return-code assertions, `wt_model_assert` comparisons at multiple read timestamps, `verify_noexcept` success/failure checks, and debug-log replay verification after close/reopen. Failures usually point to mismatched model history semantics or an instrumentation/debug-log regression rather than test harness noise.
