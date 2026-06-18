<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java

## Purpose
`ByteArrayUtil` provides tuple-layer and general byte-array helpers for concatenation, replacement, splitting, unsigned comparison, prefix ranges, integer encoding, and printable diagnostics.

## Important APIs, Types, And Functions
Important methods include `join`, `interludeJoin`, `regionEquals`, `replace`, `split`, `compareUnsigned`, `comparator`, `startsWith`, `strinc`, `keyAfter`, `encodeInt`, `decodeInt`, `printable`, and package-private `nullCount`. It extends `FastByteComparisons`.

## Control Flow
Join computes total length then copies parts and optional interludes. Replace can do a sizing pass when replacement length differs, then a writing pass into a `ByteBuffer`. Split scans for delimiters and returns copied segments. `strinc` strips trailing `0xff` then increments the last remaining byte.

## State And Persistence Behavior
All methods are stateless and allocate new arrays except methods writing into a caller-supplied `ByteBuffer`. `encodeInt`/`decodeInt` use little-endian order for FoundationDB atomic mutation operands.

## Dependencies And Integration Points
The tuple encoder uses null replacement/count helpers. Directory code uses `startsWith`, `strinc`, `join`, and `printable`. Core `KeyValue` diagnostics use printable formatting.

## Risks And Test Signals
Risks include null argument behavior, offset/length validation, delimiter edge cases, `strinc` on all-`0xff` input, `replacement == null` deletion semantics, and unsigned compare portability through `FastByteComparisons`. Tests should cover embedded zero bytes, leading/trailing delimiters, mutation operand round trips, and prefix range boundaries.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/ByteArrayUtil.java -->
