# sources/object-store/openstack-swift/swift/common/base_storage_server.py

## Purpose
`base_storage_server.py` contains shared behavior for Swift storage server controllers. It provides timing decorators for public request handlers and a base class implementing the common `OPTIONS` response for object, account, and container servers.

## Important APIs, types, and functions
- `labeled_timing_stats(metric, **dec_kwargs)` returns a decorator that passes a mutable `timing_stats_labels` dict into a controller method, captures `HTTPException` as a response, adds method/status labels, and emits `statsd.timing_since()`.
- `timing_stats(**dec_kwargs)` returns a decorator that records normal timings or `.errors.timing` based on whether the response status is a server error.
- `BaseStorageServer.__init__()` stores replication-server enablement and log anonymization settings from config.
- `BaseStorageServer.server_type` is an abstract property expected to be implemented by concrete storage servers.
- `BaseStorageServer.allowed_methods` introspects callable attributes marked `publicly_accessible`, excluding replication methods when `replication_server` is disabled.
- `BaseStorageServer.OPTIONS()` is a public timed handler returning `Allow` and `Server` headers.

## Control flow
Decorated controller methods are invoked inside wrappers that record start time, catch `HTTPException`, derive status from the returned/raised response, and emit metrics before returning the response object. `allowed_methods` lazily scans the controller once, filtering on attributes attached by Swift's `@public` decorator and optional `replication` marker, then caches a sorted method list. `OPTIONS` builds a `swob.Response` with the allowed methods and `server_type/swift_version`.

## State and persistence behavior
State is in-memory configuration and the cached `_allowed_methods` list. There is no disk persistence. Metrics are emitted externally through the controller logger or statsd client, and the response exposes Swift version and allowed API surface.

## Dependencies and integration points
The module depends on Swift version metadata, `public`, `config_true_value`, `LOG_LINE_DEFAULT_FORMAT`, server-error classification, and `swob` response/exception types. Concrete account, container, and object server controllers inherit the base class or use the decorators for timing behavior.

## Risks and edge cases
`labeled_timing_stats` reserves `method` and `status` labels; controller-provided labels with those names are overwritten. The decorator assumes the wrapped method accepts `timing_stats_labels`; applying it to a method without that keyword will break. `allowed_methods` caches results, so dynamic changes to public/replication attributes after first access are not reflected. `timing_stats` treats non-server HTTP errors as normal timings, matching Swift's metric convention but requiring careful interpretation.

## Test signals
Tests should cover public method discovery, replication method suppression, `OPTIONS` headers, timing/error metric names for 2xx/4xx/5xx responses, raised `HTTPException` handling, and labeled timing label overwrite behavior.
