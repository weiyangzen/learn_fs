# sources/storage-engines/tikv/src/import/raft_writer.rs

## Purpose
Provides asynchronous raft/engine write helpers for import apply paths, including per-region concurrency throttling when writing through thread-local engines.

## Important APIs, Types, and Functions
`wait_write` awaits the first `WriteEvent` from an async write stream and returns success only for `Finished(Ok(()))`. `ThrottledTlsEngineWriter` owns a shared `Inner` map from region id to semaphores and exposes unsafe `write<E>`, `try_gc`, and test inspection helpers. `MAX_CONCURRENCY_PER_REGION` defaults to 16.

## Control Flow
`write` records queue time, creates or reuses a region semaphore, waits for a permit, obtains the thread-local engine through `with_tls_engine`, calls `engine.async_write`, waits for completion, records apply duration and bytes, and releases the permit by dropping it. `try_gc` removes semaphore entries whose strong count shows no in-flight writer references.

## State and Persistence Behavior
The writer stores only throttle state in memory. Persistent effects are the engine writes performed by `WriteData`. It assumes the runtime worker threads have registered an engine in TLS.

## Dependencies and Integration Points
Depends on `tikv_kv::Engine`, `WriteData`, `WriteEvent`, `with_tls_engine`, tokio semaphores, importer metrics, and storage errors. `ImportSstService::do_apply` uses it to apply downloaded KV files with bounded region-level concurrency.

## Risks and Edge Cases
`write` is unsafe because the caller must guarantee the TLS engine has type `E` or compatible layout. `wait_write` treats progress events before `Finished` as unexpected errors, so async write streams used here must emit only the expected terminal event. Semaphore maps can grow by region until periodic GC runs. If a semaphore is closed, writes fail with a boxed error.

## Test Signals
Tests compare applied engine state to a mirror engine, verify per-region concurrency throttling under failpoints, and verify GC removes idle region workers. Coverage strongly targets throttling correctness and TLS-engine apply behavior.
