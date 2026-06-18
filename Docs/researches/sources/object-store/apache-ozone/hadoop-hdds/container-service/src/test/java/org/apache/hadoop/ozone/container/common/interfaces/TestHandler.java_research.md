# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/interfaces/TestHandler.java

## Purpose
`TestHandler` verifies container handler lookup through `HddsDispatcher` and `Handler.getHandlerForContainerType`. It ensures the known key-value container type resolves to `KeyValueHandler` and an invalid protobuf enum value resolves to `null`.

## Important APIs, Types, And Functions
- `Handler.getHandlerForContainerType` builds handlers by `ContainerProtos.ContainerType`.
- `HddsDispatcher.getHandler` retrieves handlers from the dispatcher map.
- `VolumeChoosingPolicyFactory.getPolicy`, `ContainerChecksumTreeManager`, `ContainerMetrics`, mocked `ContainerSet`, and mocked `VolumeSet` support handler creation.

## Control Flow
`setup` creates an `OzoneConfiguration`, mocked container/volume state, a mock datanode context, metrics, and a handler map for all known container types. The test then constructs `HddsDispatcher` with those handlers. `testGetKeyValueHandler` asks for `KeyValueContainer` and asserts the returned instance is a `KeyValueHandler`. `testGetHandlerForInvalidContainerType` uses `ContainerType.forNumber(2)` as a sentinel invalid value, asserts it is still `null`, and verifies dispatcher lookup with `null` returns `null`.

## State And Persistence Behavior
The file uses no persistent storage. Runtime state is the dispatcher handler map and global `ContainerMetrics`, which is removed in `tearDown`.

## Dependencies And Integration Points
The test depends on protobuf enum numbering, `HddsDispatcher`, `Handler`, `KeyValueHandler`, metrics lifecycle, checksum manager construction, and helper context from `ContainerTestUtils`. It protects the integration between protobuf container types and concrete datanode container handlers.

## Risks And Edge Cases
The invalid enum test intentionally guards against new `ContainerType` values occupying number 2; if a new type is added, this test should fail so handler mapping expectations are revisited. It also checks dispatcher null tolerance.

## Test Signals
The signals are direct type and null assertions. Coverage is narrow and does not execute handler methods, but it is useful for handler factory mapping.
