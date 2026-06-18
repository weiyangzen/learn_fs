# sources/storage-engines/tikv/src/coprocessor/mod.rs

Purpose: top-level coprocessor module. It documents the subsystem, declares submodules, exports endpoint/error/checksum pieces, defines request type constants, and provides shared request context and handler traits.

Important APIs/types: `RequestHandler` is the async trait implemented by cache, DAG, analyze, checksum, and test fixtures. It supports unary `handle_request`, streaming `handle_streaming_request`, scan statistics/summary collection, and boxing. `RequestHandlerBuilder<Snap>` is a one-shot closure from snapshot and `ReqContext` to boxed handler. `ReqContextInner` stores protobuf context, ranges, deadline, peer, scan direction, start ts, bypass/access lock sets, cache match version, lower/upper bounds, perf level, and flashback allowance. `ReqContext` wraps it in `Arc` and implements heap sizing. `build_task_id` combines task-id low bits with start-ts or random fallback.

State and persistence: context is immutable per request and shared across async tasks; memory trace roots for coprocessor/analyze are global process state. Dependencies include kvproto, `Deadline`, `PerfLevel`, `TsSet`, `MemoryTrace`, and storage `Statistics`.

Integration points: endpoint constructs `ReqContext`; handlers consume it; tracker/metrics use request tags; analyze uses `MEMTRACE_ANALYZE`. Risks include deadline derivation precedence (`max_execution_duration_ms` overrides config), lower/upper bound assumptions on sorted ranges, and panics if unsupported handler methods are called. Tests cover task-id composition, deadline override behavior, and constructor equivalence.
