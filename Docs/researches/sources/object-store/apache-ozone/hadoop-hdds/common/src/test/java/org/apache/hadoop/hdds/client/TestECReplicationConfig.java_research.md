# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/client/TestECReplicationConfig.java

## Purpose
This test class verifies parsing and protobuf round-trip behavior for erasure-coded replication configs.

## APIs and dependencies
It targets `ECReplicationConfig`, `ECReplicationConfig.EcCodec`, and `HddsProtos.ECReplicationConfig`. Positive examples cover `RS` and `XOR` codecs, uppercase and lowercase input, data/parity counts, raw chunk sizes, and `k` or `K` suffix conversion. Negative examples use JUnit parameterized tests and expect `IllegalArgumentException`.

## Control flow and state behavior
`testSuccessfulStringParsing` builds a map from descriptor strings to expected config objects, constructs a new config from each descriptor, and compares data, parity, codec, and chunk size fields. `testUnsuccessfulStringParsing` rejects malformed descriptors, unsupported codec strings, zero parity, zero chunk size, missing fields, and invalid short forms. `testSerializeToProtoAndBack` converts a config to protobuf and back, then checks all fields and object equality.

## Integration points
EC descriptors are used by replication config parsing, bucket and key defaults, protobuf wire formats, and client/server configuration strings.

## Risks and test signals
Parsing changes can break user-facing config strings. Unit suffix handling is especially risky because `1024k` maps to bytes, while an unsuffixed value is interpreted directly. Protobuf round trips are the compatibility signal for persisted and RPC-carried EC replication metadata.
