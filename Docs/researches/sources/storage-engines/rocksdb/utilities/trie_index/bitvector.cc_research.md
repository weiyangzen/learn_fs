# sources/storage-engines/rocksdb/utilities/trie_index/bitvector.cc

## Purpose

`bitvector.cc` implements the serialized immutable bitvector and Elias-Fano compressed monotone sequence declared in `bitvector.h`. These data structures support the experimental trie index, especially LOUDS-style rank/select navigation and compressed offset storage.

## Important APIs, types, and functions

For `Bitvector`, the implementation provides `SerializedSize`, `EncodeTo`, `InitFromData`, `BuildFrom`, `BuildRankLUT`, `BuildSelectHints`, `FindNthZeroBit`, and `DistanceToNextSetBit`. `FindNthOneBit`, `Rank1`, `NextSetBit`, and `PrevSetBit` are inline in the header for hot paths. For `EliasFano`, it implements `BuildFrom`, `SerializedSize`, `EncodeTo`, and `InitFromData`.

## Control flow and state behavior

`Bitvector::SerializedSize` computes the exact binary footprint: two fixed 64-bit header fields, raw 64-bit words, a uint32 rank LUT padded to 8 bytes, and select1/select0 hint arrays padded to 8 bytes. `EncodeTo` appends that layout with `memcpy` and zero padding for alignment. `InitFromData` parses the same layout from external memory, validates header fields (`num_ones <= num_bits`, `num_bits <= UINT32_MAX`), derives all array counts, verifies sufficient size and pointer alignment, assigns raw pointers into the caller-owned buffer, and validates select hint bounds against the rank LUT size.

`BuildFrom` creates an owned serialized-like memory block from a `BitvectorBuilder`. It first allocates words plus rank LUT, copies builder words, builds the rank LUT to discover `num_ones_`, then resizes storage to include select hints, recomputes all internal pointers, and builds hint arrays. `BuildRankLUT` writes cumulative popcounts at every 256-bit sample boundary and sets `num_ones_`. `BuildSelectHints` records the rank sample that contains every 256th one or zero. `FindNthZeroBit` uses select0 hints, scans rank samples, masks padding bits in the last word, and calls `FindNthSetBitInWord` on the inverted word. `DistanceToNextSetBit` asserts the starting position is set and returns the distance to the next set bit or the sentinel distance to `num_bits_`.

`EliasFano::BuildFrom` handles empty input by building an empty high bitvector so serialization remains consistent. For non-empty sorted values, it computes `low_bits = floor(log2(universe / count))` when useful, builds unary-coded high bits by appending gaps and one bits, and packs low bits into an owned uint64 word array. `EncodeTo` writes `count`, `universe`, `low_bits`, the high bitvector, and low words. `InitFromData` validates header fields, limits `count_` to a reasonable maximum to avoid overflow, parses the high bitvector, derives low-word size, checks size/alignment, and points `low_words_` into external memory.

## Dependencies and integration points

The file depends on `util/coding.h` for fixed-width integer encoding in Elias-Fano, `util/math.h` via the header for popcount/log operations, `port/lang.h`, `rocksdb::Status`, and raw `Slice`-compatible byte storage. It is intended for trie index metadata blocks, where serialized data may be block-cache memory and must outlive objects initialized with `InitFromData`.

## Risks and edge cases

The deserialization path is intentionally defensive but still depends on alignment guarantees from serialized buffers or block cache allocations. `Bitvector` pointers into external data become invalid if the backing slice is freed. `BuildRankLUT` asserts `num_bits_ <= UINT32_MAX`; release builds rely on earlier construction constraints or deserialization checks. Select hint correctness is critical because hints index into the rank LUT. `FindNthZeroBit` must mask padding bits in the last word so implicit zeros beyond `num_bits_` are not selectable. Elias-Fano assumes monotone input and uses assertions rather than runtime corruption errors in `BuildFrom`, so builder callers must validate ordering if data is untrusted.

## Test signals

No tests are in this file, but strong expected signals include round-trip encode/decode for empty and non-empty bitvectors, rank/select over boundary positions, zero selection in partial final words, move construction/assignment of owned data, Elias-Fano access across word-boundary low-bit packing, malformed input rejection, and alignment failure handling. Trie index seek and iteration tests should also exercise the hot rank/select paths.
