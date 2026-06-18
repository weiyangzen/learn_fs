<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/logger.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/logger.rs

## Purpose
`logger.rs` adapts tirocks environment logging into TiKV's structured logging macros for RocksDB and raft DB logs.

## Important APIs, Types, and Functions
`RocksDbLogger` and `RaftDbLogger` implement tirocks `Logger`. Each `logv` maps tirocks `LogLevel` variants to `info!`, `debug!`, `warn!`, `error!`, or `crit!`, with different log targets/keys for RocksDB versus raft DB.

## Control Flow
`logv` matches the level and converts byte log messages using `String::from_utf8_lossy`. `NUM_INFO_LOG_LEVELS` is ignored.

## State and Persistence Behavior
The loggers are stateless. They emit process logs but do not persist engine data.

## Dependencies and Integration Points
They depend on `tikv_util` logging macros and tirocks env logger traits. DB option setup can install these loggers into tirocks env/options.

## Risks and Edge Cases
Lossy UTF-8 conversion avoids panics but may obscure binary data. Fatal RocksDB logs are mapped to `crit!` but do not by themselves abort. High-volume debug/info RocksDB logs can be noisy depending on TiKV logging configuration.

## Test Signals
Tests should verify level-to-macro routing indirectly through log capture or at least ensure all tirocks log levels are handled.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/logger.rs -->
