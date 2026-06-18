<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java

## Purpose
This factory exposes native XOR raw coders to the registry.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "xor_native"`, creates `NativeXORRawEncoder` and `NativeXORRawDecoder`, and returns codec name `xor`.

## Control Flow
Factory creation is direct; exceptions are expected to be caught by higher-level fallback logic.

## State and Persistence Behavior
No factory state is retained.

## Dependencies and Integration Points
It integrates with `ServiceLoader`, `CodecRegistry`, `CodecUtil`, and mapping tests.

## Risks and Test Signals
Risks are service conflicts and ordering mistakes. Tests should assert native XOR is first in registry and Java XOR is selected after native failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->
