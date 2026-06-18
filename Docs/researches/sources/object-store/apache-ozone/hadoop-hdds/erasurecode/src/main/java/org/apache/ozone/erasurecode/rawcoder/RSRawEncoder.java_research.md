<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java

## Purpose
`RSRawEncoder` is the pure-Java Reed-Solomon encoder fallback.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder`, owns `encodeMatrix` and `gfTables`, constructs a Cauchy matrix using `RSUtil.genCauchyMatrix`, initializes GF tables for parity rows, and implements both `doEncode` overloads.

## Control Flow
Construction validates the number of units against GF(256), builds the encode matrix, optionally dumps diagnostics, and precomputes GF multiplication tables. Encode resets parity outputs to zero and calls `RSUtil.encodeData` for ByteBuffers or byte arrays.

## State and Persistence Behavior
Schema-specific matrix and GF tables persist for the encoder lifetime. No mutable per-call state is retained.

## Dependencies and Integration Points
It depends on `RSUtil`, `DumpUtil`, and `ECReplicationConfig`, is created by `RSRawErasureCoderFactory`, and is the Java fallback for RS codec operations.

## Risks and Test Signals
Risks include field-size limits, output reset omissions, and compatibility drift with native ISA-L. Tests include RS encode/decode round trips, Java/native mapping, direct and heap buffer paths, and erasure combinations from `TestRSRawCoderBase`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java -->
