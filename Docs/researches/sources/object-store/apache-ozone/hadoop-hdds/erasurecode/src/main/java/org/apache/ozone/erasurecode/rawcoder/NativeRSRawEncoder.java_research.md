<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java

## Purpose
`NativeRSRawEncoder` is Ozone's native Reed-Solomon encoder wrapper over Hadoop ISA-L support.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawEncoder`, owns Hadoop `NativeRSRawEncoder`, constructs with `ErasureCoderOptions`, implements `performEncodeImpl(...)`, `release()`, and `preferDirectBuffer()`.

## Control Flow
The base class validates and offsets inputs/outputs; this class delegates the actual encode operation to `HadoopNativeECAccessorUtil.performEncodeImpl`. Release forwards to the wrapped native object.

## State and Persistence Behavior
The wrapped native encoder may hold native tables/resources for the replication schema until released.

## Dependencies and Integration Points
It is created by `NativeRSRawErasureCoderFactory` and preferred by `CodecRegistry` before Java RS when available.

## Risks and Test Signals
Risks include native unavailability, direct/heap conversion overhead, resource lifecycle leaks, and schema mismatch. Tests include native RS parity correctness, direct/heap paths, release behavior, and Java fallback when construction fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java -->
