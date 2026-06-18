<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java

## Purpose
This factory creates pure-Java Reed-Solomon raw coders.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "rs_java"`, creates `RSRawEncoder` and `RSRawDecoder`, returns coder name, and returns codec name `rs`.

## Control Flow
Creation methods directly instantiate Java RS coders with the provided replication config.

## State and Persistence Behavior
No mutable factory state is held.

## Dependencies and Integration Points
It integrates with `CodecRegistry`, `CodecUtil` fallback, `ServiceLoader`, and tests that verify RS registry order.

## Risks and Test Signals
Risks are service registration conflicts and fallback not reaching Java RS after native failure. Tests assert registry coder names and successful RS Java coding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->
