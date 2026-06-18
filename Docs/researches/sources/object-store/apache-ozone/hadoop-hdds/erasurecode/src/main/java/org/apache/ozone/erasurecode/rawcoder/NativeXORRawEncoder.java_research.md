<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java

## Purpose
`NativeXORRawEncoder` is Ozone's wrapper around Hadoop native XOR encoding.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawEncoder`, owns Hadoop `NativeXORRawEncoder`, constructs with `ErasureCoderOptions`, implements `performEncodeImpl(...)`, and delegates `release()`.

## Control Flow
The abstract base gathers positions and locks the native path; this class forwards encode arguments to `HadoopNativeECAccessorUtil.performEncodeImpl`.

## State and Persistence Behavior
The wrapped native encoder is persistent for the Java object lifetime and must be released.

## Dependencies and Integration Points
It is created by `NativeXORRawErasureCoderFactory`, selected before Java XOR by `CodecRegistry`, and exercised by native XOR tests.

## Risks and Test Signals
Risks include native construction failure, resource leaks, and unsupported parity layouts. Test signals are native XOR encode/decode, Java fallback, direct buffer preference, and release behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java -->
