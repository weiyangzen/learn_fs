<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/db_vector.rs -->
# sources/storage-engines/tikv/components/engine_tirocks/src/db_vector.rs

## Purpose
`db_vector.rs` adapts tirocks `PinSlice` to TiKV's `engine_traits::DbVector` abstraction for zero-copy-ish point-read values.

## Important APIs, Types, and Functions
`RocksPinSlice` wraps `tirocks::PinSlice`, derives `Default`, implements `DbVector`, dereferences to `[u8]`, formats as bytes for `Debug`, and supports `PartialEq<&[u8]>`.

## Control Flow
There is no control flow beyond dereferencing and formatting. `engine.rs` fills a default `RocksPinSlice` through `Db::get_pinned`.

## State and Persistence Behavior
The wrapper owns a pinned RocksDB slice object whose lifetime is managed by tirocks. It is read-only and does not persist data.

## Dependencies and Integration Points
It is the `Peekable::DbVector` type for `engine_tirocks::RocksEngine`.

## Risks and Edge Cases
Correctness depends on tirocks `PinSlice` keeping underlying data valid for the wrapper's lifetime. `Debug` prints raw bytes, which can be noisy for large values.

## Test Signals
Point-read tests in `engine.rs` compare `RocksPinSlice` values to byte slices. Additional tests should cover missing values and debug output expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_tirocks/src/db_vector.rs -->
