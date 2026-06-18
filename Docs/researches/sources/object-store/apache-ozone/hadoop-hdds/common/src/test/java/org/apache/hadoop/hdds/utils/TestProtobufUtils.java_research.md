# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestProtobufUtils.java

## Purpose
Tests UUID conversion between Java `UUID` and HDDS protobuf UUID representation.

## Important APIs, types, and functions
- Uses `ProtobufUtils`, `HddsProtos.UUID`, and Java `UUID`.
- Test cases are `testUuidToProtobuf` and `testUuidConversion`.

## Control flow
The tests create UUID values, convert to protobuf, inspect most/least-significant bit fields, convert back, and assert equality.

## State and persistence behavior
The protobuf representation models persisted or wire-format UUID state. No actual store is used.

## Dependencies and integration points
UUID conversion is used across HDDS protobuf APIs for datanodes, pipelines, and other identifiers.

## Risks and test signals
Swapping UUID bit order would corrupt identity matching. These tests signal exact bit-preserving conversion.
