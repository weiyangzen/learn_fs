<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java

## Purpose
`CodecUtil` creates raw encoders and decoders for an `ECReplicationConfig`, trying registered coder factories in priority order with fallback.

## Important APIs, Types, and Functions
It exposes `createRawEncoderWithFallback(ECReplicationConfig)` and `createRawDecoderWithFallback(ECReplicationConfig)`, plus private `createRawCoderFactory(String,String)`.

## Control Flow
For a config, it lowercases the codec enum name, fetches coder names from `CodecRegistry`, iterates in order, and tries to create a coder. It catches `LinkageError` and `Exception`, logs at debug, and tries the next coder. If all fail, it throws `IllegalArgumentException`.

## State and Persistence Behavior
The utility is stateless; registry state is external.

## Dependencies and Integration Points
It depends on `CodecRegistry`, raw coder factories, `ECReplicationConfig`, and SLF4J. It is the main integration point for native-first then Java fallback selection.

## Risks and Test Signals
Risks include `null` coder name arrays causing NPE for unknown codecs, swallowing important construction errors at debug level, and fallback order relying on registry correctness. Tests assert RS/XOR native-vs-Java selected types and unknown/invalid registry behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java -->
