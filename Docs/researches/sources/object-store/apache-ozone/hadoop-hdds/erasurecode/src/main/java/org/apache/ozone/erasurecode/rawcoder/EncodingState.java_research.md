<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java

## Purpose
`EncodingState` is the shared base for raw encoder per-call validation.

## Important APIs, Types, and Functions
It stores `RawErasureEncoder encoder` and `int encodeLength`. Its generic `checkParameters(T[] inputs, T[] outputs)` validates data input count and parity output count.

## Control Flow
Validation compares input length to `encoder.getNumDataUnits()` and output length to `encoder.getNumParityUnits()` before subclass buffer checks.

## State and Persistence Behavior
The state is transient per encode call.

## Dependencies and Integration Points
It is extended by `ByteArrayEncodingState` and `ByteBufferEncodingState` and gates every public encode entry point.

## Risks and Test Signals
Risks are limited validation scope: this class does not check nulls or lengths. Tests should cover bad input/output counts and subclass-specific buffer validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java -->
