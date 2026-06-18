# sources/storage-engines/tikv/components/server/src/setup.rs

Purpose: central startup setup utilities for logging, metrics, command-line config overrides, validation, and fatal process termination. It is used before and during server startup so failures are reported consistently even before the logger is initialized.

Important APIs and functions: `fatal!` logs through slog when `LOG_INITIALIZED` is true, otherwise writes to stderr, clears the global logger, and exits. `initial_logger` builds normal, RocksDB, raftdb, and optional slow-log drains, selecting text or JSON format and terminal or file output. `initial_metric` starts process, thread, and allocator metric monitors and warns that metrics push is unsupported. `overwrite_config_with_cmd_args` maps CLI arguments into `TikvConfig`. `validate_and_persist_config` delegates validation/persistence and aborts on failure. `ensure_no_unrecognized_config` aborts if unknown config keys remain.

Control flow: log setup computes RocksDB and raftdb info log paths via configured info-log directories or data dir, creates needed directories, canonicalizes paths, creates rotating file writers using `rename_by_timestamp`, builds a `LogDispatcher`, and initializes global logging with slow-log threshold. CLI override handling updates log, server addresses, data dir, PD endpoints, labels, capacity, and metrics warning in place.

State and persistence behavior: this file creates log directories and rotating log files. `rename_by_timestamp` renames rotated files using local timestamp. Config validation may persist configuration through `tikv::config::validate_and_persist_config` depending on the `persist` flag. It also sets global redaction behavior and `LOG_INITIALIZED`.

Dependencies and integration points: relies on `tikv_util::logger`, `tikv_util::config`, `chrono`, `clap::ArgMatches`, and TiKV config types. Server startup imports this module and `fatal!` is used broadly in `server2.rs`.

Risks: process exit is immediate and not recoverable. Timestamp-based rotation has a documented small duplicate-name risk under intense rotation. Path conversion uses `to_str().unwrap_or_else(fatal!)`, so non-UTF8 paths terminate startup. Label parsing is strict and rejects malformed `key=value` entries.

Test signals: no direct unit tests in this file. Behavior is exercised through startup/config tests elsewhere; failpoint `mock_force_uninitial_logger` covers the stderr fallback path.
