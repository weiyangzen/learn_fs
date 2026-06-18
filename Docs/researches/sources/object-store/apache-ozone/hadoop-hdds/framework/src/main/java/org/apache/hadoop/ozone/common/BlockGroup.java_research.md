# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/BlockGroup.java

## Purpose

`BlockGroup` represents deleted blocks associated with one object key/group and converts between Java objects and SCM `KeyBlocks` protobufs. The complete 121-line source was read for this report.

## Important APIs, Types, and Functions

Fields are `groupID` and `List<DeletedBlock>`. APIs include `getDeletedBlocks`, `getGroupID`, `getProto`, static `getFromProto`, `newBuilder`, `toString`, and nested `Builder` methods `setKeyName`, `addAllDeletedBlocks`, and `build`.

## Control Flow

`getProto` iterates deleted blocks, adding block IDs and size fields to a `KeyBlocks.Builder`. `getFromProto` iterates protobuf block entries, reading optional size arrays by index and defaulting missing size, replicated size, or size-per-replica to `SIZE_NOT_AVAILABLE`.

## State and Persistence Behavior

The class is an in-memory DTO. Serialized protobufs may be persisted or sent over SCM protocols by callers.

## Dependencies and Integration Points

It depends on `BlockID`, `DeletedBlock`, and `ScmBlockLocationProtocolProtos.KeyBlocks`. It integrates with block deletion workflows between Ozone metadata and SCM.

## Risks and Edge Cases

The builder does not validate null group ID or deleted block list. `getFromProto` assumes block count drives all optional parallel size lists. Missing size data is represented as `-1`.

## Test Signals

Tests should cover proto round trips with full and missing size fields, empty block lists, null builder inputs if allowed by callers, and preservation of block IDs and sizes.
