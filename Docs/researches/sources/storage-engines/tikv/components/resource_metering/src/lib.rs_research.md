# sources/storage-engines/tikv/components/resource_metering/src/lib.rs

## Purpose
`lib.rs` is the public surface of the `resource_metering` crate. It re-exports collector/config/model/recorder/reporter APIs and implements request tagging wrappers that attach resource metering context to futures and streams through thread-local storage.

## Important APIs, Types, And Functions
`ResourceMeteringTag` holds `Arc<TagInfos>` and a `ResourceTagFactory`. `attach` registers thread-local storage with the recorder if needed, rejects nested attachments in debug builds, stores the tag in `STORAGE`, resets the per-request summary record, and returns a `Guard`.

`Guard::drop` clears the attached tag, optionally merges summary metrics into `summary_records`, ignores disabled summaries and empty extra tags, drops zero-read/logical records, and caps retained summary maps at `MAX_SUMMARY_RECORDS_LEN`.

`ResourceTagFactory` creates tags from RPC context, optionally with key ranges, and registers thread-local `LocalStorageRef`s with the recorder scheduler. `FutureExt` and `StreamExt` wrap async work in `InTags<T>`, whose `poll`/`poll_next` attaches the tag for the duration of each poll. `TagInfos` extracts store, peer, region, key ranges, and resource group tag bytes from `kvproto::kvrpcpb::Context`.

## Control Flow
Callers create a tag from request context, then call `.in_resource_metering_tag(tag)` on a future or stream. Each poll attaches the tag to thread-local storage, allowing recorder sampling to attribute CPU and summary counters to the current request. When the poll returns, the guard drops and clears the tag while aggregating summary counters.

## State And Persistence Behavior
State is thread-local in recorder `STORAGE`, plus shared summary maps protected by `Mutex`. Registration retries are capped by `MAX_THREAD_REGISTER_RETRY`. The crate does not persist data directly; reporter/recorder modules handle downstream transport.

## Dependencies And Integration Points
This file integrates with recorder registration, reporter data sinks/pubsub/single-target APIs, `kvproto` contexts, `tikv_util::worker::Scheduler`, `thread::thread_id`, `HeapSize`, `pin-project`, and `core_intrinsics::unlikely`.

## Risks
Nested attachment is only debug-asserted and returns a guard without replacing the tag, so nested async instrumentation can silently skip attribution in release builds. `SharedTagInfos::load_full` in local storage uses swap-based access, so guard drop spin-waits until the tag is available. Summary maps are capped to prevent unbounded growth if recorder cleanup fails, which means new tags can be dropped under high cardinality.

## Test Signals
`test_attach` creates a thread-local tag, verifies it is visible during attachment, and verifies the tag is cleared after guard drop.
