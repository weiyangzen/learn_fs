<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java

## Purpose

`DispatcherContext` carries transport-specific execution metadata from gRPC/Ratis server code into `ContainerDispatcher` and command handlers. It identifies the operation phase, write-chunk stage, Ratis term/index, container-to-BCSID map, start time, and optional release hook. The complete 266-line file was read.

## Important APIs, Types, and Functions

Static singleton accessors cover common non-Ratis handle operations: read chunk/block, write chunk, get small file, and put small file. `WriteChunkStage` values are `WRITE_DATA`, `COMMIT_DATA`, and `COMBINED` with `isWrite()`/`isCommit()` helpers. `Op` values distinguish handle, state-machine read/write/apply, stream init/link, and null operations. `Op.readFromTmpFile()` and `Op.validateToken()` encode handler policy. Builder methods set stage, term, log index, container map, and release support.

## Control Flow

The file is mostly data construction. Callers create a builder for an `Op`, optionally set Ratis metadata and stage, then pass the context to `ContainerDispatcher`. Dispatcher or lower layers can inspect `DispatcherContext.op(context)` safely when context is null. Release support is opt-in; `setReleaseMethod` asserts support, and `release()` invokes the stored hook if present.

## State and Persistence Behavior

Each instance is immutable except the volatile `releaseMethod`. It persists no data, but carries a mutable map reference for container BCSID tracking when supplied by the Ratis state machine.

## Dependencies and Integration Points

It integrates with `ContainerDispatcher`, gRPC read contexts, `ContainerStateMachine`, Ratis `TermIndex`, and token-validation logic in container handlers.

## Risks and Edge Cases

The static singleton contexts do not support release hooks and have default term/index zero. `validateToken()` returns false for apply/write/read state-machine data and stream link because tokens were validated earlier; using the wrong op can skip needed token validation. The container map is not copied, so callers share mutation semantics.

## Test Signals

Tests should verify token-validation policy by op, write-stage helper semantics, null-safe `op`, release assertion and invocation, and that Ratis contexts carry term/index/container map into command handlers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/transport/server/ratis/DispatcherContext.java -->
