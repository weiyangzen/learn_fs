# sources/storage-engines/tikv/src/coprocessor/cache.rs

Purpose: implements the fast coprocessor-cache hit path. `CachedRequestHandler` is a trivial `RequestHandler` used when the request carries a cache match version equal to the snapshot data version. Instead of building and executing DAG/analyze/checksum logic, it returns a `coprocessor::Response` marked `is_cache_hit`.

Important APIs: `CachedRequestHandler::new` reads `SnapshotExt::get_data_version`; `builder` returns a `RequestHandlerBuilder`; `handle_request` sets `is_cache_hit` and optionally `cache_last_version`. Control flow is intentionally one step: endpoint selects this handler, then the handler returns an empty data response with cache metadata.

State and persistence: the only stored state is optional `data_version`. It is not persisted and is derived from the read snapshot. Dependencies are `tikv_kv::SnapshotExt`, `tikv_alloc::MemoryTraceGuard`, and the coprocessor `RequestHandler` trait.

Integration points: selected by `Endpoint::handle_unary_request_impl` when `ReqContext.cache_match_version` matches `snapshot.ext().get_data_version()`. Risks are mostly semantic: cache-hit responses must preserve version metadata and must not be used for non-matching versions. Test signals are indirect through endpoint cache behavior; this file has no local tests.
