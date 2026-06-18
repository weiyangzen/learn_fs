<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java

## Purpose
This factory exposes native Reed-Solomon raw coders to the registry.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "rs_native"`, creates `NativeRSRawEncoder` and `NativeRSRawDecoder`, returns coder name, and returns codec name `rs`.

## Control Flow
Factory methods instantiate native wrappers; any native linkage failure is surfaced to `CodecUtil`, which can fall back to Java RS.

## State and Persistence Behavior
No mutable state is owned.

## Dependencies and Integration Points
It integrates with Java `ServiceLoader`, `CodecRegistry` native-first ordering, `ECReplicationConfig.EcCodec.RS`, and codec mapping tests.

## Risks and Test Signals
Risks include service-registration conflicts and native factory precedence breaking fallback. Tests assert registry order and native/Java mapping depending on native availability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->
