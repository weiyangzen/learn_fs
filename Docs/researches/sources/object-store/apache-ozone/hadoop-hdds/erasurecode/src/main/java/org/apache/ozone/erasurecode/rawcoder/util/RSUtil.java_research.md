<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java

## Purpose
`RSUtil` contains ISA-L-derived Reed-Solomon matrix/table generation and bulk encode routines.

## Important APIs, Types, and Functions
It exposes `GF`, `PRIMITIVE_ROOT`, `getPrimitivePower`, `initTables`, `genCauchyMatrix`, and `encodeData` overloads for byte arrays and ByteBuffers.

## Control Flow
`genCauchyMatrix` writes an identity data section and Cauchy parity rows. `initTables` builds 32-byte GF vector tables for each coding coefficient. `encodeData` loops over outputs and inputs, selects a GF multiplication table line, XORs table lookups into outputs in 8-byte chunks, then handles leftover bytes.

## State and Persistence Behavior
It is stateless except for using `GaloisField` and `GF256` static tables. Callers own matrix/table arrays.

## Dependencies and Integration Points
It is used by `RSRawEncoder` and `RSRawDecoder` for both encoding and decoding.

## Risks and Test Signals
Risks include incorrect matrix offsets, output buffers not reset before XOR accumulation, byte signedness errors, and performance regressions in the inner loops. Test signals include RS known erasure patterns, native compatibility, direct/heap buffers, odd data lengths, and different data/parity configurations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java -->
