<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java

## Purpose
`XORRawEncoder` is the pure-Java XOR parity generator.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder` and implements both ByteBuffer and byte-array encode paths.

## Control Flow
Encoding resets the first output, copies the first input into it, then XORs every remaining input into the same output. ByteBuffer operations use absolute get/put so caller positions are advanced only by the base class.

## State and Persistence Behavior
No mutable state is retained.

## Dependencies and Integration Points
It is created by `XORRawErasureCoderFactory` and tested through `TestXORRawCoderBase`.

## Risks and Test Signals
Risks include assuming a single parity output and all inputs being non-null. Tests should verify parity regeneration for different erased data indexes, parity erasure, direct and heap buffers, and too-many-erasure failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java -->
