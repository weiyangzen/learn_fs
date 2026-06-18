<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs

## Purpose
Implements erasure-coded reads from bitrot-protected shard streams. It reads shard blocks in parallel, tolerates missing or corrupt shards up to the erasure limit, reconstructs missing data shards, and writes a requested byte range into an async output writer.

## Important APIs, types, and functions
`ParallelReader<R>` owns a vector of optional `BitrotReader<R>` values plus shard offset, shard size, shard-file size, data shard count, and total shard count. `ParallelReader::read` reads one erasure block across readers until it has enough successful shards. `ParallelReader::can_decode` checks read quorum. `get_data_block_len` sums available data-shard bytes. `write_data_blocks` writes a range from decoded data shards to the target writer. `Erasure::decode` is the public async read path for a requested `offset`, `length`, and `total_length`.

## Control flow
`Erasure::decode` first validates that the reader count equals `data_shards + parity_shards`, rejects `offset + length` overflow or ranges past `total_length`, and returns immediately for zero length. It constructs a `ParallelReader` positioned to the start block. The loop spans `start = offset / block_size` through `end = (offset + length - 1) / block_size`; each iteration computes the in-block offset and length for start, middle, and final blocks.

For each block, `ParallelReader::read` computes the current shard block length from `offset`, `shard_size`, and `shard_file_size`, then creates one future per reader. Missing readers immediately return `FileNotFound`; present readers call `BitrotReader::read`. It initially polls only `data_shards` futures and starts additional shard reads only when an earlier one fails, stopping once it has `data_shards` successes. `Erasure::decode` records the first reducible `FileNotFound` or `FileCorrupt`, fails with `ErasureReadQuorum` if fewer than `data_shards` shards are available, reconstructs with `decode_data`, and calls `write_data_blocks` to emit the requested range. If no hard error occurred but fewer bytes than requested were written, it returns `LessData`.

`write_data_blocks` validates that the data-shard slice is long enough, checks `offset + length` for overflow, ensures the available data block length covers the requested range, then skips whole shards until the offset lands and writes the requested slices with `write_all`.

## State and persistence behavior
This module does not write persistent state. It interprets the persistent shard layout established by `BitrotWriter` and `Erasure::shard_file_size`. `ParallelReader` holds stream readers and advances them one framed shard block per `read` call; the production caller must seek/open readers at the correct shard-file offset before constructing it. Error state is returned per block as a vector of optional disk errors and summarized by `reduce_errs`.

## Dependencies and integration points
Depends on `crate::disk::error::Error`, `crate::disk::error_reduce::reduce_errs`, `BitrotReader`, and `Erasure`. It uses `futures::stream::FuturesUnordered` for bounded parallel reads, `tokio::io::AsyncRead/AsyncWrite`, and tracing for error logging. It calls `Erasure::decode_data`, so its parity/backend behavior is controlled by `erasure.rs`.

## Risks and test signals
Because `ParallelReader` stops after enough successful reads, errors on later shards may remain unobserved in healthy reads; this is good for latency but can hide latent corruption until those shards are needed. `ParallelReader::offset` is initialized from the starting block but is not incremented inside `read`, so repeated calls rely on reader stream advancement for data and use the same final-block sizing calculation; this works for normal full-size middle blocks but is a risk area for edge cases near shard-file tails. Range math is guarded against overflow, but callers must ensure readers are pre-positioned consistently with the requested offset.

Tests cover ranged reads across block boundaries, compressed stream preservation behind the `rio-v2` feature, write-range helper errors, normal parallel reads, offline disks, and bitrot-corrupt disks. The ranged-read regression test explicitly documents that `Erasure::decode` does not seek readers itself.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs -->
