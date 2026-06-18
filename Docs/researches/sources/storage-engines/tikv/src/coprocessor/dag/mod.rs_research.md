# sources/storage-engines/tikv/src/coprocessor/dag/mod.rs

Purpose: bridges TiKV coprocessor DAG requests into the TiDB query executor runner. It builds batch DAG handlers, adapts extra-region storage access, and converts query-engine results/errors into coprocessor protobuf responses.

Important APIs/types: `DagHandlerBuilder<R,S,F>` captures request, ranges, store, optional extra-region accessor, deadline, batch limits, paging, max-keys-read, cache flags, and quota limiter. `build` increments the DAG request metric and returns a boxed `BatchDagHandler`. `ExtraTiKVStorageAccessor<R>` wraps a `RegionStorageAccessor` and converts its storage into `TikvStorage`. `BatchDagHandler::new` calls `BatchExecutorsRunner::from_request`; its `RequestHandler` impl delegates unary and streaming execution and exposes scan stats/summary.

Control flow: endpoint parses DAG protobuf, constructs `DagHandlerBuilder`, then the handler runner executes DAG batches. `handle_qe_response` serializes `SelectResponse`, sets returned range and cache metadata, maps storage errors to coprocessor errors, maps deadline to `Error::DeadlineExceeded`, and embeds evaluate errors inside the select response. `handle_qe_stream_response` performs the analogous streaming conversion for `StreamResponse`.

State is request-local except runner-held scan/cache state. Dependencies are `tidb_query_executors`, `tidb_query_common`, API-version key formats, quota limiter, and coprocessor metrics. Risks include error-shape compatibility with TiDB, cacheability correctness across extra-region reads, and the interaction of paging/max-keys limits. Local tests cover response conversion, storage/deadline/evaluate error mapping, and cache metadata.
