# sources/storage-engines/tikv/src/server/config.rs

## Purpose

`server/config.rs` defines TiKV server-layer configuration, default values, validation, and online update handling. It covers network endpoints, gRPC concurrency and memory, raft client queues, snapshot concurrency and IO limits, coprocessor endpoint limits, status server options, request batching, memory-based message rejection, health feedback, slow-store network inspection, graceful shutdown, and store labels.

The file is the main boundary between static TOML configuration, online config updates, gRPC resource quota resizing, snapshot worker refresh, and coprocessor config dispatch.

## Important APIs, types, and functions

`GrpcCompressionType` is a serde-friendly mirror of grpc-rs compression algorithms. `Config` derives `OnlineConfig` and uses `serde(rename_all = "kebab-case")`. Many identity, listener, concurrency, and deprecated endpoint fields are marked `#[online_config(skip)]`, while selected runtime tunables such as `max_grpc_send_msg_len`, snapshot limits, `grpc_memory_pool_quota`, endpoint memory quota, `snap_io_max_bytes_per_sec`, `snap_max_total_size`, graceful shutdown timeout, and hidden/simplified metrics fields remain online configurable.

`Config::default` computes CPU-aware defaults. `DEFAULT_GRPC_RAFT_CONN_NUM` is `floor(cpu_quota / 8)` clamped to 1..4, and `DEFAULT_GRPC_CONCURRENCY` is three times that value plus two. Endpoint memory quota defaults to 12.5 percent of available memory but at least 500 MB. Endpoint max concurrency is at least four.

`Config::validate` normalizes advertise addresses, rejects invalid listener combinations, enforces nonzero snapshot and gRPC memory values, checks endpoint recursion and max-handle duration, validates gRPC send/window sizes, validates labels, checks forward connection count and memory reject ratio, migrates too-large legacy `heavy_load_threshold` to 75, checks network inspection interval lower bound, warns on disabled graceful shutdown timeout, and enforces raft connection/queue size consistency.

`grpc_compression_algorithm`, `end_point_request_max_handle_duration`, and `optimize_for` are helper APIs used by server construction and region-size based tuning.

`ServerConfigManager` implements `ConfigManager`. It applies online changes to an `Arc<VersionTrack<Config>>`, resizes the gRPC `ResourceQuota` when `grpc_memory_pool_quota` changes, schedules `SnapTask::RefreshConfigEvent`, and forwards the change to the coprocessor config manager.

`validate_label_key` and `validate_label_value` enforce Kubernetes-style-ish label syntax using regexes. Keys may optionally start with `$` but otherwise must begin and end with alphanumeric characters; values may be empty and allow `-A-Za-z0-9_./`.

## Control flow

Startup constructs `Config::default`, deserializes user config over it, then calls `validate`. Validation may mutate defaults: empty `advertise_addr` falls back to `addr`, non-unspecified status address may become `advertise_status_addr`, and legacy heavy-load thresholds above 100 are reset to 75.

Online updates enter `ServerConfigManager::dispatch`. The manager clones the incoming `ConfigChange`, applies it through `VersionTrack::update`, separately resizes the grpc-rs quota if the memory quota field changed, schedules snapshot config refresh best-effort, dispatches to the coprocessor manager best-effort, logs errors for side-effect failures, and returns success unless the version-track update itself fails.

`optimize_for` adjusts `end_point_request_max_handle_duration` only if it is unset. Regions below 256 MB use the 60 second default; larger regions scale by region-size multiples capped at 1800 seconds.

## State and persistence behavior

The configuration itself is in-memory once loaded, but it originates from persisted config files or online config sources outside this file. `VersionTrack<Config>` stores live server config snapshots. `ResourceQuota::resize_memory` mutates grpc-rs runtime quota in place. Snapshot and coprocessor changes are propagated through schedulers/managers; this file does not write RocksDB or raft state.

Validation mutates `Config` values before use, so callers should treat `validate` as both checking and normalizing.

## Dependencies and integration points

This module depends on `tikv_util::config` helpers, `SysQuota`, grpc-rs `CompressionAlgorithms` and `ResourceQuota`, `online_config`, raftstore store config exports, storage config exports, snapshot tasks, coprocessor config manager, and `engine_traits::PerfLevel` serde helpers. It is consumed by the server bootstrap path, online config controller, snapshot subsystem, gRPC server setup, coprocessor endpoint setup, raft client setup, and status server setup.

## Risks and edge cases

Address normalization has important semantics: unspecified `0.0.0.0` can be a valid bind address but invalid advertise address, so fallback is conditional. `advertise_status_addr` must not equal `advertise_addr`. `grpc_memory_pool_quota` is cast to `usize` during validation and resize; extremely large values need platform awareness. `reject_messages_on_memory_ratio` rejects negative values but permits values above 1.0, which may be intentional but weakly bounded. Online dispatch logs snapshot/coprocessor dispatch failures but still returns `Ok`, so operators may see partial application.

Deprecated endpoint fields remain in the struct for compatibility and are hidden/skipped for online config. Label regexes are stricter for keys than values, which tests document.

## Test signals

`test_config_validate` covers advertise fallback, default CPU-derived gRPC values, nonzero limits, recursion limit, memory quota, max-handle duration, invalid bind/advertise cases, duplicate advertise addresses, gRPC message/window limits, and label value validation. `test_store_labels` exercises key/value regex edge cases including empty strings, prefixes/suffixes, `$`, path separators, and non-ASCII input.
