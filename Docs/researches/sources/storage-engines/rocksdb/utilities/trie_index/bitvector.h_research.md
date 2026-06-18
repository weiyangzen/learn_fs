# sources/storage-engines/rocksdb/utilities/trie_index/bitvector.h

## Purpose

`bitvector.h` declares the experimental trie-index succinct bitvector and Elias-Fano structures. `Bitvector` stores immutable bits with O(1) rank/select, next/previous set-bit search, and serialization support. `BitvectorBuilder` incrementally builds the bit stream. `EliasFano` compresses monotonically non-decreasing uint64 sequences while supporting O(1) random access.

## Important APIs, types, and functions

Constants `kBitsPerRankSample = 256`, `kWordsPerRankSample = 4`, and `kOnesPerSelectHint = 256` define lookup-table granularity. Utility functions include `Popcount`, `Ctz`, `CtzNonZero`, and `FindNthSetBitInWord`, with a BMI2/PDEP fast path on x86_64 when available and a portable popcount binary search fallback.

`BitvectorBuilder` exposes `Append`, `AppendWord`, `AppendMultiple`, `Reserve`, `GetBit`, `NumBits`, and `Words`. `Bitvector` deletes copy, implements move with pointer reseating, and exposes `InitFromData`, `EncodeTo`, `BuildFrom`, `GetBit`, `Rank1`, `Rank0`, `FindNthOneBit`, `FindNthZeroBit`, `NextSetBit`, `PrevSetBit`, `DistanceToNextSetBit`, `NumBits`, `NumOnes`, `NumZeros`, and `SerializedSize`. Private helpers build rank/select metadata and recompute internal pointers after moves.

`EliasFano` deletes copy, implements move with low-word pointer reseating, and exposes `BuildFrom`, `InitFromData`, `EncodeTo`, `Access`, `Count`, `Universe`, and `SerializedSize`.

## Control flow and state behavior

`BitvectorBuilder` appends bits LSB-first into uint64 words. `AppendMultiple` optimizes runs by filling a partial trailing word, appending full words, then appending a final partial word. `AppendWord` is for word-aligned bulk append, especially 256-bit dense-node label maps.

`Bitvector` has two ownership modes. `BuildFrom` allocates `owned_data_` and points `words_`, `rank_lut_`, and select hints into it. `InitFromData` points those raw pointers into external serialized memory, and the caller must keep that memory alive. Copying is deleted because raw pointers could dangle; moving is supported and reseats pointers into `owned_data_` when owned storage is non-empty. Rank uses a uint32 cumulative LUT at 256-bit boundaries plus unrolled popcount over up to three whole words and one partial word. Select uses hints to narrow to a small rank-sample range and scans words with popcount. Next/previous set-bit functions use trailing-zero and floor-log operations with sentinel `num_bits_` for not found.

`EliasFano` stores high bits as a `Bitvector` with one bits at `high[i] + i`, and low bits packed into uint64 words. `Access(i)` selects the i-th high one, subtracts `i` to recover the high part, extracts `low_bits_` bits from `low_words_`, handles cross-word extraction, and combines high and low. Like `Bitvector`, initialized-from-data instances point into external memory, while built instances own low-bit storage.

## Dependencies and integration points

The header depends on RocksDB portability/math helpers (`BitsSetToOne`, `CountTrailingZeroBits`, `FloorLog2`), `rocksdb::Slice`, `rocksdb::Status`, and standard vector/string storage. It is a foundational component for trie-index metadata, likely used by dense/sparse LOUDS trie structures for label bitmaps, child navigation, and compressed offsets.

## Risks and edge cases

Most API contracts are enforced with assertions, so callers must respect preconditions in release builds: positions must be in bounds, `AppendWord` must be word-aligned, Elias-Fano input must be monotone, and `Access` requires `i < count_`. External-memory initialization is lifetime-sensitive. `Rank1(pos)` permits `pos == num_bits_`, but relies on a sentinel rank sample and valid word access only when a partial word is present. `Access` includes an explicit guard against shifting by 64 when low bits start on a word boundary. The uint32 rank LUT limits bitvectors to `UINT32_MAX` bits, which the comments argue is far above realistic trie-index sizes.

## Test signals

Expected tests should cover builder append variants, rank and select at sample boundaries, all-ones/all-zeros vectors, partial final words, next/previous set-bit sentinel behavior, serialization round trips, move construction/assignment with small and large owned strings, external-buffer lifetime usage, and Elias-Fano empty, dense, sparse, duplicate, and word-crossing cases.
