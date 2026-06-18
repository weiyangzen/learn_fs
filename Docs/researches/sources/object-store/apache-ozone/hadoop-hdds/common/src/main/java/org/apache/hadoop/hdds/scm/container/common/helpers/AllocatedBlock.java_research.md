# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/common/helpers/AllocatedBlock.java

## Purpose
Return value for SCM block allocation, pairing the selected pipeline with the allocated `ContainerBlockID`.

## Important APIs, Types, And Functions
`AllocatedBlock` exposes `getPipeline`, `getBlockID`, static `newBuilder`, and `toBuilder`. Nested `Builder` sets `Pipeline` and `ContainerBlockID`.

## Control Flow
Block allocation code builds an `AllocatedBlock` after selecting/creating a container and pipeline; callers use the pipeline for writes and block ID for metadata.

## State And Persistence
The object is immutable after construction and transient. Persistence of the block ID occurs in OM/key metadata and container state outside this class.

## Dependencies And Integration Points
Depends on `ContainerBlockID` and `Pipeline`. Integrated by SCM allocate-block APIs and client write paths.

## Risks And Test Signals
Builder does not validate null fields. Tests should cover allocation responses, `toBuilder`, and downstream handling of missing pipeline/block IDs.
