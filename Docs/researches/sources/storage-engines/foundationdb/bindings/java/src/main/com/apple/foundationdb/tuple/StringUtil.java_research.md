<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java -->
# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java

## Purpose
`StringUtil` validates UTF-16 strings and computes tuple-compatible UTF-8 ordering and packed sizes.

## Important APIs, Types, And Functions
Package-private methods are `validate`, `compareUtf8`, `packedSize`, and `adjustForSurrogates`. It defines fixed error messages for high/low surrogate malformations.

## Control Flow
Validation scans for well-formed surrogate pairs. `compareUtf8` skips a common prefix, then adjusts surrogate-range code units so Java UTF-16 comparison aligns with Unicode code point/UTF-8 byte ordering. `packedSize` counts encoded UTF-8 bytes and extra null escaping.

## State And Persistence Behavior
The class is stateless and non-instantiable. No database persistence occurs, but its output determines tuple key byte layout.

## Dependencies And Integration Points
`TupleUtil` calls `validate` before string encoding, `packedSize` for buffer sizing, and `compareUtf8` for semantic tuple comparison without packing.

## Risks And Test Signals
Risks include incorrect surrogate ordering, malformed UTF-16 acceptance/rejection, and packed-size mismatch causing buffer overflow. Tests should cover ASCII, null characters, BMP non-ASCII, supplementary code points, isolated high/low surrogates, and compare consistency with packed byte order.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/tuple/StringUtil.java -->
