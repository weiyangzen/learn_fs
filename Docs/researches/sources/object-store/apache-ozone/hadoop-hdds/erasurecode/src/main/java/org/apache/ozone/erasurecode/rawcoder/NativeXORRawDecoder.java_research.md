<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java

## Purpose
`NativeXORRawDecoder` adapts Ozone XOR decode calls to Hadoop's native XOR raw decoder.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawDecoder`, owns Hadoop `NativeXORRawDecoder`, constructs with `ErasureCoderOptions`, implements `performDecodeImpl(...)`, and delegates `release()`.

## Control Flow
The base class validates decode state and calculates offsets, then this class calls `HadoopNativeECAccessorUtil.performDecodeImpl` on the wrapped native decoder.

## State and Persistence Behavior
The wrapped native decoder holds native resources until `release()`.

## Dependencies and Integration Points
It is created by `NativeXORRawErasureCoderFactory` and used by codec fallback for XOR.

## Risks and Test Signals
Risks include native library absence, XOR parity count assumptions, and release lifecycle errors. Tests include native XOR availability assumptions and decode-after-release behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java -->
