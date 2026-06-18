# sources/storage-engines/rocksdb/util/prefix_varint.h

## Purpose
Implements a little-endian prefix-varint encoding where the number of trailing zero bits in the first byte determines encoded length. It is designed for callers that can read one byte first and then fetch the remaining bytes, and for potentially faster in-memory decoding than continuation-bit varints.

## Important APIs, Types, And Functions
Constants define maximum lengths: `kMaxPrefixVarint32Length == 5`, `kMaxPrefixVarint64Length == 9`, and the invalid 32-bit additional-byte sentinel. `PrefixVarint32Length` and `PrefixVarint64Length` compute minimal encoded length. `EncodePrefixVarint32`, `EncodePrefixVarint64<kMinimumBytes>`, `PutPrefixVarint32`, and `PutPrefixVarint64` encode values into buffers or strings. `PrefixVarint32AddlByteCount` and `PrefixVarint64AddlByteCount` support split reads. `DecodePrefixVarint32`, `DecodePrefixVarint64`, `GetPrefixVarint32Ptr`, `GetPrefixVarint64Ptr`, `GetPrefixVarint32`, and `GetPrefixVarint64` decode from byte spans or `Slice`.

## Control Flow
Encoding computes the number of bytes from the highest set bit, shifts payload bits left by the encoded length, and sets the prefix marker bit. `PrefixVarint64` switches to a special nine-byte form when the first byte is zero, followed by fixed64 payload bytes. Decoding optimizes the one-byte case, then determines required additional bytes from the first byte, assembles a little-endian encoded word, shifts off the prefix bits, and validates 32-bit overflow where applicable. Slice adapters advance only after successful decoding.

## State And Persistence
All functions are stateless inline helpers. The encoded bytes are durable data format state for any caller that persists them. The format is intentionally distinct from RocksDB's continuation-bit varints; compatibility must be explicit at call sites.

## Dependencies And Integration Points
Depends on `rocksdb/slice.h`, `util/coding_lean.h` for fixed64 encode/decode, `util/math.h` for `FloorLog2` and trailing-zero counts, `util/cast_util.h`, and branch prediction macros. It can integrate with storage or block-format code that wants length-known-after-first-byte reads.

## Risks
Format confusion with existing varint helpers would corrupt decoding. `DecodePrefixVarint64` treats first byte zero as the valid nine-byte form and fails only for insufficient bytes; callers must enforce canonical encoding if needed. Non-minimal 64-bit encodings are possible through `kMinimumBytes`, so consumers should not assume minimality unless the producer contract guarantees it. Inline byte-at-a-time load/store has TODO performance caveats.

## Test Signals
No assigned direct test, but the API is written with explicit boundary checks for truncated inputs, invalid 32-bit prefixes, and uint32 overflow. Future tests should cover canonical lengths, all boundary transitions, the 9-byte uint64 path, Slice no-advance-on-failure behavior, and non-minimal `kMinimumBytes` encoding.
