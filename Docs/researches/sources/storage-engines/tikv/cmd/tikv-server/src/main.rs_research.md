# sources/storage-engines/tikv/cmd/tikv-server/src/main.rs

## Purpose
`tikv-server/src/main.rs` is the production TiKV server entrypoint. It handles early FIPS setup, version metadata, CLI parsing, config loading/overrides/checking, logging, memory initialization, optional async tracing, and dispatch to the correct server implementation by storage engine type.

## Important APIs, Types, And Functions
- `main()` is the only function.
- CLI options include config path, config check/info, log level/file, listen and advertise addresses, status addresses, data directory, capacity, PD endpoints, labels, sample config printing, and a hidden metrics push address.
- It uses `TikvConfig::from_file`, `server::setup::overwrite_config_with_cmd_args`, `logger_compatible_adjust`, `validate_and_persist_config`, `ensure_no_unrecognized_config`, `to_flatten_config_info`, `initial_logger`, and `config.storage.validate_engine_type`.
- Runtime launch calls `server::server::run_tikv` for `EngineType::RaftKv` and `server::server2::run_tikv` for `EngineType::RaftKv2`.

## Control Flow
The entrypoint enables FIPS immediately, builds version strings, defines clap arguments, and handles `--print-sample-config` before loading any user config. It records unrecognized config keys only for `--config-check`. After command-line overrides and logger compatibility adjustment, `--config-check` validates and exits, while `--config-info json` prints flattened config metadata and exits. Normal startup validates storage engine type, optionally initializes async-backtrace tracing, initializes logging, logs version/FIPS status, initializes memory settings, creates a service event channel, and starts the selected server implementation.

## State And Persistence Behavior
The server process will own all TiKV persistent state after `run_tikv`, but this file itself only reads config and may persist validated config via `validate_and_persist_config` in config-check mode. It initializes global logger, memory settings, optional tracing subscriber, and service event channel.

## Dependencies And Integration Points
This entrypoint is a coordinator for the `server` and `tikv` crates. It integrates with Clap, FIPS crypto, serde_json config-info output, TiKV config validation, memory initialization, and storage-engine-specific server modules.

## Risks And Edge Cases
- Panics on invalid config file loading are intentional but can be abrupt.
- `config-info` only accepts JSON and exits before runtime validation beyond loading/overrides.
- Engine-type validation must happen before server startup because it can adjust engine type.
- Optional tracing is compile-time feature gated; missing feature means no active-tree layer.

## Test Signals
Server startup integration tests and config validation tests provide coverage. CLI paths worth testing include sample config, config check with unknown keys, config-info JSON, engine type validation, and command-line override precedence.
