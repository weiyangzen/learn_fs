<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java

## Purpose
`NativeRSRawDecoder` adapts Ozone replication config to Hadoop's native Reed-Solomon decoder backed by ISA-L.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawDecoder`, owns a Hadoop `NativeRSRawDecoder`, constructs it with `ErasureCoderOptions`, implements `performDecodeImpl(...)`, `release()`, and `preferDirectBuffer()`.

## Control Flow
Construction creates the Hadoop native decoder. Decode calls arrive through the abstract base, which supplies offsets and length to `HadoopNativeECAccessorUtil.performDecodeImpl`. Release delegates to the Hadoop native decoder.

## State and Persistence Behavior
Persistent process state is the wrapped native decoder and its native resources until `release()`.

## Dependencies and Integration Points
It integrates with `NativeRSRawErasureCoderFactory`, `CodecUtil` fallback order, Hadoop native EC accessor utilities, and native RS tests.

## Risks and Test Signals
Risks include native library absence, release-after-use errors, mismatched erased indexes, and config translation mistakes. Tests cover native RS data/parity erasure combinations, native skip when unavailable, and decode after release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java -->
