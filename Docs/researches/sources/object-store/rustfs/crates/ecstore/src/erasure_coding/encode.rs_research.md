<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs

## Purpose
Implements erasure-coded writes from an async reader into bitrot-protected shard writers. It handles Reed-Solomon encoding, bounded producer/consumer buffering, write quorum enforcement, metrics for in-flight encoded data, and small-object fast paths.

## Important APIs, types, and functions
`MultiWriter<'a>` coordinates a mutable slice of optional `BitrotWriterWrapper` values, tracks per-writer errors, and enforces a write quorum for writes and shutdown. `MultiWriter::write_shard`, `write`, `shutdown_writer`, and `shutdown` are the core write fanout. `Erasure::encode` is the main streaming pipeline. `Erasure::encode_inline_small` and `encode_single_block_non_inline` use `encode_small_direct` to avoid the task/channel pipeline for small data. `encode_channel_capacity`, `queued_block_bytes`, and `drain_queued_inflight_bytes` bound and clean up encode buffering. Formatting helpers turn `WriteQuorumFailureSummary` into stable error and metric labels.

## Control flow
`Erasure::encode` rejects zero `block_size`, computes expanded encoded block bytes as `shard_size * total_shard_count`, reads `RUSTFS_ERASURE_ENCODE_MAX_INFLIGHT_BYTES` with a 32 MiB default, and creates a bounded MPSC channel capped at 32 encoded blocks. A spawned producer task repeatedly reads full blocks with `rustfs_utils::read_full_or_eof`, encodes each block on `tokio::task::spawn_blocking`, adds encoded byte count to `rustfs_io_metrics`, and sends the encoded block vector to the consumer. It maps checksum-mismatch-flavored unexpected EOFs to `InvalidData`.

The consumer wraps writers in `MultiWriter`, receives encoded blocks, removes the corresponding in-flight metric, and calls `writers.write`. On write error it aborts the producer task, awaits it, drains any queued metric bytes, attempts writer shutdown, and returns the write error. If the stream completes cleanly, it awaits the producer result and shuts down writers, returning the original reader and total plaintext bytes read.

`MultiWriter::write` concurrently writes each shard to writers that do not already have an error. A short write marks that writer failed; a missing writer is `DiskNotFound`. It succeeds once non-error writers meet `write_quorum`; otherwise it reduces errors with `reduce_write_quorum_errs`, emits an internode metric labelled by dominant error, logs the full error vector, and returns a summarized `io::Error`. `shutdown` applies the same quorum accounting to flush/shutdown. `encode_small_direct` reads all data or one bounded block, encodes via `encode_data_owned`, writes once through `MultiWriter`, then shuts down.

## State and persistence behavior
This module writes persistent shard streams through `BitrotWriterWrapper`: encoded shard bytes become bitrot-framed blocks on each disk or remote writer. It mutates writer state by setting failed writer slots to `None` after short writes or shutdown failures and by retaining `errs` across blocks, so a writer that fails once is skipped for later blocks. In-flight metrics are incremented when encoded blocks enter the queue and decremented on receive or drain, making abort cleanup part of correctness.

## Dependencies and integration points
Depends on `disk::error` and `disk::error_reduce` for quorum semantics, `BitrotWriterWrapper` and `Erasure` for shard writing and encoding, `futures::FuturesUnordered` for concurrent fanout, `tokio::sync::mpsc`, `rustfs_utils` for env parsing and full-block reads, `rustfs_rio` for checksum mismatch identification, and `rustfs_io_metrics` for memory/quorum telemetry. The functions integrate with object write paths that supply shard writers and quorum values.

## Risks and test signals
The streaming producer owns the reader inside a spawned task, so cancellation paths must correctly abort, await, and drain metrics. A writer error causes shutdown to be attempted but returns the original write error, meaning shutdown failures are logged but secondary. `MultiWriter::write` asserts data/writer length equality instead of returning an error, so callers must maintain exact shard counts. `encode_inline_small` returns without shutting down writers for empty streams, which tests assert; callers must be prepared for no commit on empty input. The single-block fast path deliberately reads `block_size + 1` and rejects oversized input.

Tests cover shutdown after small shards, truncated limited readers, zero block size rejection, inline empty and payload behavior, single-block payload and oversized rejection, channel capacity edge cases, and stable write-quorum summary labels. Additional high-value tests would simulate producer encode failure after queued blocks and verify in-flight metric cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs -->
