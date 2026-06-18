# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerListResult.java

## Purpose
Wrapper for paginated container-list responses, carrying the current page of `ContainerInfo` objects and the total matching count.

## Important APIs, Types, And Functions
Constructor takes `List<ContainerInfo>` and `long totalCount`. Getters expose both fields.

## Control Flow
SCM list APIs create this object after querying container metadata and counting total matches.

## State And Persistence
The wrapper is transient and does not copy the list, so list mutability is inherited from the caller.

## Dependencies And Integration Points
Depends on `ContainerInfo`. Integrated by SCM client/admin APIs and pagination consumers.

## Risks And Test Signals
List aliasing can surprise callers. Tests should cover total-count correctness, empty pages, and response serialization.
