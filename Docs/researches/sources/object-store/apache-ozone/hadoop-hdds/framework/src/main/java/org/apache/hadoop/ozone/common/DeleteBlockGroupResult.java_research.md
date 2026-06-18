# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/ozone/common/DeleteBlockGroupResult.java

## Purpose

`DeleteBlockGroupResult` captures the result of deleting all blocks for an object key and converts block deletion results to/from SCM protobuf result messages. The complete 95-line source was read for this report.

## Important APIs, Types, and Functions

APIs include constructor, `getObjectKey`, `getBlockResultList`, `getBlockResultProtoList`, static `convertBlockResultProto`, `isSuccess`, and `getFailedBlocks`.

## Control Flow

`getBlockResultProtoList` maps each `DeleteBlockResult` into a `DeleteScmBlockResult` protobuf. `convertBlockResultProto` maps protobufs back to helper results. `isSuccess` returns false on the first non-success result. `getFailedBlocks` streams and collects block IDs whose result is not `Result.success`.

## State and Persistence Behavior

The object is an in-memory result DTO. Protobuf conversion allows RPC or persistence by callers.

## Dependencies and Integration Points

It depends on `BlockID`, SCM block location protobufs, and `DeleteBlockResult`. It integrates with SCM block deletion command/result paths.

## Risks and Edge Cases

Constructor does not defensively copy the result list. Empty lists count as success. Null lists or null result entries would fail at use time.

## Test Signals

Tests should cover all-success, partial-failure, empty-list, proto round trip, and failed block extraction.
