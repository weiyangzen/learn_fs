<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java

## Purpose
`XORRawDecoder` is the pure-Java XOR decoder fallback.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder` and implements ByteBuffer and byte-array `doDecode` methods.

## Control Flow
Each decode resets the single output buffer, reads the first erased index, then XORs all non-erased input units into the output using absolute buffer/array accesses.

## State and Persistence Behavior
It owns no mutable state beyond inherited config.

## Dependencies and Integration Points
It is created by `XORRawErasureCoderFactory` and used as fallback for XOR codec operations.

## Risks and Test Signals
Risks include assuming one output/parity style, null inputs beyond the erased index causing failures, and invalid erased indexes. Tests include data and parity erasure cases, too many erasures, and Java/native XOR mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java -->
