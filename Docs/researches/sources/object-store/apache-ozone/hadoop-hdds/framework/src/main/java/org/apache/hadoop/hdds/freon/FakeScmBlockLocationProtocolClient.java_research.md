# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/freon/FakeScmBlockLocationProtocolClient.java

## Purpose

This utility returns fake `SCMBlockLocationResponse` protobufs for Freon block-allocation load tests. It avoids real SCM calls while producing plausible SCM info and container block IDs.

## Important APIs, Types, and Functions

`submitRequest(SCMBlockLocationRequest)` handles `Type.GetScmInfo` and `Type.AllocateScmBlock`. `BLOCK_PER_CONTAINER` controls container ID derivation, and a static `AtomicLong counter` provides monotonically increasing local IDs.

## Control Flow

For `GetScmInfo`, the method returns fixed `scm-id` and `cluster-id`. For `AllocateScmBlock`, it loops over `numBlocks`, increments the counter, assigns `containerID = seq / BLOCK_PER_CONTAINER`, sets `localID = seq`, and attaches a random fake pipeline. Unsupported commands throw inside the try block, are logged, and return `null`.

## State and Persistence Behavior

The only mutable state is the process-wide atomic block counter. There is no persistence.

## Dependencies and Integration Points

It depends on SCM block-location protobufs and `FakeClusterTopology`. Freon clients can use it as a static protocol shim.

## Risks and Test Signals

Returning `null` after errors pushes failure handling to callers and differs from normal RPC exception semantics. Container IDs start at zero until the counter reaches 1000. Tests should cover `GetScmInfo`, multi-block allocation, monotonic IDs under concurrency, and unsupported command behavior.
