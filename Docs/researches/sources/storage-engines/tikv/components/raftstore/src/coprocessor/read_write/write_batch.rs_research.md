# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/write_batch.rs

## Purpose
`write_batch.rs` wraps an engine `WriteBatch` so raftstore can mirror write operations into an optional observable write batch for external observers while still writing through the real engine batch.

## Important APIs, Types, And Functions
`WriteBatchObserver` creates a boxed `ObservableWriteBatch`. `ObservableWriteBatch` extends `WriteBatch + Send` and adds `prepare_for_region`, `write_opt_seq`, and `post_write`. `WriteBatchWrapper<WB>` holds the real batch plus optional observable batch and implements both `WriteBatch` and `Mutable`.

## Control Flow
`prepare_for_region` delegates to the observable batch only. Mutations (`put`, `put_cf`, `delete`, `delete_cf`, `delete_range`, `delete_range_cf`) first mirror the operation into the observable batch, then apply it to the real batch. `write`, `write_opt`, and `write_callback_opt` delegate to the real batch; inside the real write callback the wrapper calls observable `write_opt_seq` once with the engine sequence number and options, then calls the caller callback. After write completion, `post_write` is invoked on the observable batch whether the real write succeeded or failed according to the returned result path.

Save points, rollback, pop, and clear are mirrored into both batches. `merge` is intentionally unsupported and panics if called.

## State And Persistence Behavior
The wrapper does not own persistence but sits directly on the write path. The real `WB` controls engine persistence; the observable batch records a parallel stream for consumers. The `AtomicBool` in `write_callback_opt` guards against multiple callback invocations causing multiple sequence notifications.

## Dependencies And Integration Points
Uses `engine_traits::{WriteBatch, Mutable, WriteOptions, CF_DEFAULT}` and `kvproto::metapb::Region`. `CoprocessorHost::on_create_apply_write_batch` constructs this wrapper from the registry singleton write-batch observer.

## Risks
Observable mutation happens before the real mutation, so if the real operation fails, the observable batch must tolerate rollback or post-write cleanup. `merge` is not supported; callers needing merge semantics must avoid wrapping or implement explicit merging. The overridden `put_msg`/`put_msg_cf` intentionally route through `put`/`put_cf` to avoid missed observations, but this assumes no underlying implementor relies on specialized message encoding behavior beyond protobuf bytes.

## Test Signals
No direct tests in this file. Expected coverage is through downstream write-batch observer implementations and raftstore apply-write paths that use `on_create_apply_write_batch`.
