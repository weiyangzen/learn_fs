# sources/storage-engines/tikv/src/server/status_server/mod.rs

## Purpose

This module implements TiKV's HTTP status server. It exposes operational endpoints for metrics, readiness, configuration inspection and online update, profiling, log level changes, region metadata, resource groups, gRPC pause/resume, in-memory-engine inspection, async task traces, failpoints in failpoint builds, and forced partition ranges. It is also responsible for optional TLS wrapping and certificate common-name authorization on sensitive endpoints.

## Important APIs, Types, And Functions

`StatusServer<R>` owns the status runtime, shutdown channel, bound address, `ConfigController`, raft router, `SecurityConfig`, optional `ResourceGroupManager`, `GrpcServiceManager`, optional `RegionCacheMemoryEngine`, and `ForcePartitionRangeManager`. `new` builds a dedicated Tokio runtime with status-server thread naming and system hooks. `start` binds `AddrIncoming`, records the real local address, conditionally wraps incoming sockets with TLS, and calls `start_serve`. `stop` signals graceful shutdown and waits up to three seconds for the runtime.

Endpoint helpers include `get_config`, `update_config`, `update_config_from_toml_file`, `get_engine_type`, `change_log_level`, `metrics_to_resp`, `handle_ready_request`, `dump_heap_prof_to_resp`, `dump_cpu_prof_to_resp`, `get_cmdline`, `get_symbol_count`, `get_symbol`, `dump_region_meta`, `handle_get_all_resource_groups`, `handle_dumple_cached_regions`, `dump_async_trace`, and force partition range add/remove/dump helpers. `decode_json` converts flat JSON objects into string-valued config changes and rejects arrays or non-object roots. `make_response` centralizes status/body construction.

TLS support is split through `ServerConnection`, `check_cert`, `tls_acceptor`, `tls_incoming`, and `TlsIncoming<S>`. The TLS accept loop reloads certificate context when SSL creation or handshake errors suggest the underlying files may have changed.

## Control Flow

`start_serve` captures the shared server dependencies, builds a Hyper `make_service_fn`, and handles every request in a `service_fn`. The handler records method and path, optionally handles failpoint routes first, decides whether certificate authorization is needed, dispatches on `(method, path)`, and records request duration using a normalized path label of `unknown` for misses. Most handlers return `hyper::Result<Response<Body>>` and convert domain errors into HTTP status codes and text bodies.

Configuration flow is `POST /config` -> collect body -> `decode_json` -> `ConfigController::update` or `update_without_persist` based on the `persist` query parameter. `PUT /config/reload` asks the controller to reload from the TOML file and intentionally tolerates non-online items according to the hosting-platform comment.

Profiling flow is `GET /debug/pprof/heap` -> heap profile temp file -> optional `jeprof` SVG transform. CPU profiling parses `seconds` and `frequency`, detects protobuf output by content type, waits through `GLOBAL_TIMER_HANDLE.delay`, and delegates single-profile enforcement and report generation to `profile.rs`.

Region and debug endpoints bridge to runtime subsystems: `dump_region_meta` asks the raft extension router for region metadata and serializes it as JSON; resource groups are flattened into debug settings; cached in-memory regions are collected from `RegionCacheMemoryEngine` under a read lock and sorted by range.

## State And Persistence Behavior

The server stores only runtime state: its Tokio runtime, optional shutdown receiver, bound address, and cloned handles to other subsystems. Persistent changes happen through `ConfigController::update` when `persist=true`; with `persist=false`, changes are applied in memory only. `update_config_from_toml_file` reads the configured TOML source. Force partition ranges mutate `ForcePartitionRangeManager` with a fixed TTL of 3600 seconds. TLS certificate state includes a local `cert_last_modified_time` used to decide whether to reload the `SslContext`.

## Dependencies And Integration Points

The module integrates Hyper/Tokio for HTTP serving, OpenSSL/tokio-openssl for TLS, Prometheus dumping, TiKV config management, raftstore metadata querying through `RaftExtension`, resource control, service-manager gRPC controls, in-memory region cache, failpoints, active async tracing, and TiKV security common-name matching. Metrics are emitted through `STATUS_REQUEST_DURATION`; readiness is sourced from `GLOBAL_SERVER_READINESS`.

## Risks And Edge Cases

Sensitive endpoints are protected only when TLS certificate common-name allowlists are configured; `/metrics`, `/status`, `/config` GET, and CPU profile GET bypass certificate checks by design. `decode_json` accepts only flat scalar JSON values, so nested online config updates are impossible through this path unless represented as dotted keys. `get_symbol` accepts arbitrary posted addresses and resolves them in-process, which is operationally useful but sensitive. TLS reload occurs only after handshake/setup errors, not proactively. Force partition range errors include misspelled messages and always add ranges with 3600-second TTL. Unknown paths are collapsed for metrics cardinality, but real route labels for dynamic `/region/<id>` are not normalized before the route match unless unknown.

## Test Signals

The module has broad unit/integration tests: status and metrics endpoints, config get/update with persist and non-persist modes, failpoint endpoints with and without the feature, TLS common-name authorization, heap and CPU profiling, pprof symbol resolution, gzip metrics, log-level update, engine type reporting, gRPC pause/resume error behavior with dummy manager, readiness verbose JSON, and in-memory-engine cached-region dumping.
