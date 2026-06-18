# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/DeletedBlocksTransactionInfoWrapper.java

## Purpose

This wrapper provides JSON-friendly and conversion-friendly representation of deleted-block transaction info.

## Important APIs, Types, and Functions

It stores `txID`, `containerID`, `localIdList`, and `count`, exposes Jackson `@JsonCreator` constructor and getters, and converts among `DeletedBlocksTransactionInfo`, wrapper, and datanode `DeletedBlocksTransaction`.

## Control Flow

`fromProtobuf` returns a wrapper only if txID, containerID, and count are present; otherwise it returns null. `toProtobuf`, `fromTxn`, and `toTxn` rebuild the corresponding protobufs with local IDs and count.

## State and Persistence Behavior

The wrapper is immutable in field references, but `localIdList` is not defensively copied. Persistence is external through JSON/protobuf consumers.

## Dependencies and Integration Points

It bridges SCM `HddsProtos.DeletedBlocksTransactionInfo`, datanode protocol `DeletedBlocksTransaction`, and Jackson serialization.

## Risks and Test Signals

Returning null for incomplete protobufs can surprise callers. Mutable list aliasing can change wrapper contents after construction. Tests should cover all conversions, incomplete input, JSON round trip, and list immutability expectations.
