# sources/storage-engines/tikv/components/tidb_query_datatype/src/codec/data_type/bit_vec.rs

## Purpose
Provides a compact boolean vector used as null/validity bitmaps in chunked column vectors.

## Important APIs, Types, And Functions
`BitVec` stores `Vec<u64>` plus logical `length`. Methods include `with_capacity`, `push`, `replace`, `len`, `is_empty`, `truncate`, `capacity`, `append`, and `get`. `BitAndIterator` streams the row-wise AND of multiple bitmaps.

## Control Flow
Bits are appended at `length & 63`, extending `data` by one word as needed. `replace` and `get` assert index bounds and use masks. `append` pushes every bit from the source then truncates the source to zero. `BitAndIterator` validates equal lengths, computes one 64-bit AND word every 64 rows, then shifts out booleans one by one.

## State And Persistence
In-memory only. `length` can be smaller than physical capacity. Truncation discards full trailing words but does not clear unused bits in the last retained word.

## Dependencies And Integration Points
Used by all `ChunkedVec*` implementations as validity/null bitmaps and by `ChunkRef::get_bit_vec` consumers.

## Risks
Bounds violations panic. `append` is O(n) over bits rather than word-level merging. `BitAndIterator` indexes `data[idx]` and assumes every bitmap has enough storage for its logical length; malformed `BitVec` construction would panic.

## Test Signals
Local tests cover capacity, length, push combinations, boundary alignment, replace combinations, append, truncate, and bitwise-AND iteration.
