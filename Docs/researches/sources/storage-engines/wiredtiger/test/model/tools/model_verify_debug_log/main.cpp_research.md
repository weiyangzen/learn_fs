# sources/storage-engines/wiredtiger/test/model/tools/model_verify_debug_log/main.cpp

## Purpose
This standalone tool verifies a WiredTiger database by reconstructing model state from the table debug log or from a JSON debug-log dump, then comparing that reconstructed state with the database and optionally a named checkpoint.

## Important APIs, Types, and Functions
The key function is `verify_timestamps`, which compares WT `query_timestamp` results for oldest and stable timestamps with the reconstructed `model::kv_database`. `main` parses `-C`, `-c`, `-h`, `-j`, and `-?`, opens the database read-only, lists tables with `model::wt_list_tables`, loads state with `model::debug_log_parser::from_debug_log` or `from_json`, resolves an optional checkpoint, and calls `db.table(t)->verify(conn, ckpt)` for each table.

## Control Flow
The tool builds a connection config starting from `readonly=true,log=(enabled=false)` and appends any `-C` overrides. It opens WT, loads tables and debug-log model state inside exception-handled blocks, validates global timestamps, then verifies each table. Errors print a specific diagnostic and exit failure; `-?` prints usage and exits success.

## State, Persistence, and Integration
The tool does not mutate the database. It depends on WT table debug logging having captured enough information for reconstruction. With `-j`, it can verify a JSON log produced by other tooling instead of reading the log from the open database. Checkpoint verification routes through the model checkpoint object so historical snapshot state can be compared with a named WT checkpoint.

## Risks and Test Signals
Risks include opening with incompatible read-only config, missing or incomplete debug-log metadata, table-name mismatches, timestamp formatting/parsing drift, and checkpoint names absent from the reconstructed model. Test signals are explicit table verification messages, oldest/stable timestamp mismatch errors, parser load failures, and `verify` exceptions for table or checkpoint divergence.
