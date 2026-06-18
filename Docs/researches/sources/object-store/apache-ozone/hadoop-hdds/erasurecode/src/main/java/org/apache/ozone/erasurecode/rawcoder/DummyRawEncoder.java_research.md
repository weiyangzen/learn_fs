<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java

## Purpose
`DummyRawEncoder` is the no-op encoder paired with the dummy raw coder factory.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder`, provides a constructor, and overrides `doEncode(ByteArrayEncodingState)` and `doEncode(ByteBufferEncodingState)` with no work.

## Control Flow
Framework validation and input position advancement still occur in `RawErasureEncoder`; only parity generation is skipped.

## State and Persistence Behavior
It owns no state.

## Dependencies and Integration Points
It integrates with `DummyRawErasureCoderFactory` and dummy coder tests.

## Risks and Test Signals
Risk is accidental use as a real encoder, which would produce unchanged parity outputs. Tests should keep dummy usage explicit and verify no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java -->
