## sources/storage-engines/rocksdb/table/block_based/block_util.h

Purpose: provides hot-path utility decoders for block entries and keys, including format-version-4 index-block variants, plus a big-endian key reader used for interpolation/uniformity logic.

Important APIs/types: `DecodeEntry` decodes shared key bytes, non-shared key bytes, value length, and optional separated-KV value offset. `DecodeKey` discards value length for key-only parsing. `DecodeKeyV4` decodes format-v4 entries where value length is omitted. `DecodeEntryV4` adapts v4 key decoding for entry interfaces with value length set to zero. `ReadBe64FromKey()` extracts up to eight bytes from a key at an offset as an order-preserving big-endian integer.

Control flow: decoders first attempt a fast one-byte varint path for small values, then fall back to bounded `GetVarint32Ptr()` parsing. They return `nullptr` on malformed/truncated input, allowing iterators to surface corruption. `ReadBe64FromKey()` strips internal key trailer when requested, clamps offset to key size, uses endian swap for eight-byte fast path, and zero-pads shorter suffixes.

State and persistence behavior: stateless utilities interpreting persisted block bytes. Their behavior defines how block entries written by `BlockBuilder` are read by `Block`, index iterators, footer/uniformity scanning, and corruption checks.

Dependencies/integration points: depends on internal-key constants, platform endian helpers, `Slice`, coding utilities, and math helpers. `BlockBuilder::GetRestartKey()` uses `DecodeKey`/`DecodeKeyV4`; block iterators use these decoders for normal reads.

Risks: fast-path preconditions must match caller checks; `DecodeEntry` asserts at least three bytes whereas `DecodeKeyV4` explicitly checks. Separated-KV callers must pass a `value_offset` pointer only when the entry format includes it. Internal-key reads assert enough bytes when stripping trailers.

Test signals: `block_test.cc` corruption tests exercise boundary failures; interpolation and uniformity tests exercise `ReadBe64FromKey()` behavior through `BlockBuilder` and iterators.
