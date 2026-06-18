# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/MockBlockAllocator.java

## Purpose
`MockBlockAllocator` is a test interface for generating OM `KeyLocation` entries for new keys without SCM. It lets unit tests plug in different pipeline/block allocation strategies for RATIS or EC scenarios.

## Important APIs, Types, And Functions
The single method `allocateBlock(KeyArgs createKeyRequest, ExcludeList excludeList)` returns an iterable of `KeyLocation` protobuf objects. Implementations in this subset include `SinglePipelineBlockAllocator` and `MultiNodePipelineBlockAllocator`.

## Control Flow
The interface has no implementation control flow. Callers, especially `MockOmTransport`, invoke it during create-key and allocate-block request handling.

## State And Persistence Behavior
No state is defined at the interface level. Implementations maintain block counters, cached pipelines, or cluster-node cursors.

## Dependencies And Integration Points
It depends on OM protobuf `KeyArgs`/`KeyLocation` and SCM `ExcludeList`. It integrates the in-memory OM mock with client output streams that expect OM to return allocated blocks.

## Risks And Edge Cases
Implementations must honor enough of `KeyArgs` and `ExcludeList` to match the test being run. If an implementation ignores exclusion, EC retry tests can pass incorrectly or fail for the wrong reason.

## Test Signals
All client write tests using `MockOmTransport` indirectly depend on this contract. EC retry tests provide the strongest signal because they validate exclude-aware block reallocation.
