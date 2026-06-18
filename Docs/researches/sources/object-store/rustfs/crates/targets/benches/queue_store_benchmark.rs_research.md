# sources/object-store/rustfs/crates/targets/benches/queue_store_benchmark.rs

## Purpose
Criterion benchmark for `QueueStore` raw payload write/read throughput with compression off and on.

## Important APIs and Functions
`BenchEvent` is a representative serializable payload shape. `bench_dir` creates unique temp directories. `build_payload` creates JSON payloads of requested sizes with metadata and repeated content. `queue_store_write_benchmark` measures `QueueStore::put_raw` followed by `del`. `queue_store_read_benchmark` stores one payload and repeatedly measures `get_raw`. `criterion_group!` and `criterion_main!` register both groups.

## Control Flow and State
Each benchmark case creates a new queue store under a temp directory, opens it, runs Criterion iterations, and calls `store.delete()` afterward. Write cases delete each key inside the measured iteration, so the measurement includes delete overhead.

## Integration Points
Uses `rustfs_targets::store::{QueueStore, Store}`, serde JSON, UUIDs, Criterion throughput metadata, and `Arc` for shared read benchmark state.

## Risks
Temp cleanup is best-effort and may leave directories if a benchmark panics. Write benchmark measures put plus delete rather than pure put. Payload construction uses string slicing by byte count over ASCII content, which is safe here but would not be for arbitrary UTF-8. Compression is represented as snap on/off through `new_with_compression`.

## Test Signals
This is not a correctness test; it provides performance signals for 512 B, 8 KiB, and 64 KiB payloads, each with compression disabled/enabled for raw put/get.
