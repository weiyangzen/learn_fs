<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java

## Purpose
This factory registers/creates the dummy raw coder pair for tests or placeholder codec wiring.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "dummy_dummy"` and `DUMMY_CODEC_NAME = "dummy"`, and implements `createEncoder`, `createDecoder`, `getCoderName`, and `getCodecName`.

## Control Flow
Factory methods instantiate new dummy encoder/decoder instances using the provided `ECReplicationConfig`.

## State and Persistence Behavior
No mutable state is kept; all instances are created on demand.

## Dependencies and Integration Points
It is visible to the registry if included as a service provider and is directly used by dummy coder tests.

## Risks and Test Signals
Risks include coder-name conflicts in `CodecRegistry` and accidental production exposure. Test signals include registry conflict handling, factory type assertions, and dummy encode/decode no-op tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->
