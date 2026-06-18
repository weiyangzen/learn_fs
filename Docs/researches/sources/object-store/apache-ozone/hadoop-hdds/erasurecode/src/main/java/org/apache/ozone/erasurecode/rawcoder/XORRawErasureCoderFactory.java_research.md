<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java

## Purpose
This factory creates pure-Java XOR raw coders.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "xor_java"`, and creates `XORRawEncoder`/`XORRawDecoder` for codec `xor`.

## Control Flow
Factory creation is direct and stateless.

## State and Persistence Behavior
No mutable state is retained.

## Dependencies and Integration Points
It is registered through service loading and used by codec fallback and mapping tests.

## Risks and Test Signals
Risks include wrong codec names and registry conflicts. Tests assert XOR factory ordering and successful Java XOR round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->
