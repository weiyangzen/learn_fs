<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java

## Purpose
`RawErasureCoderFactory` is the service-provider contract for raw erasure coder implementations.

## Important APIs, Types, and Functions
It declares `createEncoder(ECReplicationConfig)`, `createDecoder(ECReplicationConfig)`, `getCoderName()`, and `getCodecName()`.

## Control Flow
There is no implementation flow; `CodecRegistry` discovers implementations and `CodecUtil` invokes factories in priority order.

## State and Persistence Behavior
Factories decide their own state; the interface owns none.

## Dependencies and Integration Points
It depends on `ECReplicationConfig` and is implemented by RS, XOR, native, and dummy factories.

## Risks and Test Signals
Risks include duplicate coder names per codec, factories throwing during creation, and inconsistent codec names. Tests verify registry conflict handling, names, and factory-created types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java -->
