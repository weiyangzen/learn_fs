<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs

## Purpose
Implements erasure healing: reconstructs missing or selected shard files from available bitrot-protected shard readers and writes the rebuilt shards through bitrot writers.

## Important APIs, types, and functions
The file adds `Erasure::heal`. It accepts mutable optional `BitrotWriterWrapper` slots for target shards, a vector of optional `BitrotReader<R>` inputs, `total_length`, and an unused `_prefer` slice. It uses `decode::ParallelReader` to read available shard blocks and `encode::MultiWriter` to write reconstructed shard blocks.

## Control flow
`heal` logs the writer/reader counts and total length, then rejects writer slices whose length does not equal `data_shards + parity_shards`. It constructs a `ParallelReader` from the readers and computes the number of erasure blocks from `total_length` and `block_size`. Write quorum is set to the count of available writers, with a minimum of one, so all provided repair targets must be writable.

For each block, `ParallelReader::read` returns optional shard buffers and per-shard errors. `heal` counts successful shards and returns an error if fewer than `data_shards` are available. If parity exists, it calls `decode_data_and_parity`, reconstructing both missing data shards and missing parity shards. It converts every shard option to `Bytes`, using an empty default for any still-missing shard, and writes the full shard vector through `MultiWriter`. After all blocks, it calls `writers.shutdown`.

## State and persistence behavior
Healing writes reconstructed shard data back to the provided writer slots in the same bitrot-framed format used by normal encoding. It does not choose disks or persist metadata itself; caller-provided writer presence controls which shards are repaired. Because write quorum equals available writer count, a single repair writer failure fails the heal. `_prefer` is currently ignored, so no preferred source/target selection state affects reconstruction.

## Dependencies and integration points
Depends on `crate::disk::error::{Error, Result}`, `BitrotReader`, `BitrotWriterWrapper`, `ParallelReader`, `MultiWriter`, `bytes::Bytes`, `tokio::io::AsyncRead`, and tracing. It integrates directly with `erasure.rs` reconstruction logic and the same write quorum machinery used by `encode.rs`.

## Risks and test signals
The function validates writer count but not reader count explicitly; `ParallelReader` can work with the supplied reader vector, but mismatched lengths could lead to unexpected shard vectors. Mapping `None` shards to empty `Bytes` after reconstruction should be safe only if reconstruction filled all needed positions; if a backend leaves parity missing unexpectedly, empty shards may be offered to writers. The ignored `_prefer` parameter suggests incomplete parity/source preference behavior. `end_block` divides by `block_size`, so zero block size would panic.

Tests cover rebuilding a missing parity shard and rebuilding a missing data shard across multiple blocks, using inline writers and no checksum to compare healed bytes with original encoded shards.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs -->
