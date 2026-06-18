# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeletedBlock.java

## Purpose

`DeletedBlock` is a DTO for a block pending or involved in deletion, carrying block identity and size accounting. The complete 65-line source was read for this report.

## Important APIs, Types, and Functions

Constructor arguments are `BlockID`, `size`, `replicatedSize`, and `sizePerReplica`. Getters expose each field, and `toString` prints container/local ID and sizes.

## Control Flow

There is no complex flow beyond string formatting.

## State and Persistence Behavior

It is an in-memory DTO. Values may be serialized through `BlockGroup.getProto`.

## Dependencies and Integration Points

It depends on `BlockID` and integrates with `BlockGroup` and delete block workflows.

## Risks and Edge Cases

There is no validation for null block ID or negative size sentinel values. `toString` dereferences nested block ID fields and will fail if block ID is null.

## Test Signals

Tests should verify getters, string formatting, sentinel sizes, and `BlockGroup` serialization of size fields.
