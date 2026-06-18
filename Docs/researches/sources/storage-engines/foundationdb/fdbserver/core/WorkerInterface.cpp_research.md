# sources/storage-engines/foundationdb/fdbserver/core/WorkerInterface.cpp

## sources/storage-engines/foundationdb/fdbserver/core/WorkerInterface.cpp

Purpose: adapts a full cluster-controller interface stream into the client-facing `ClusterInterface` async variable needed by clients and dependent actors.

Important API: `extractClusterInterface`.

Control flow and state: the actor loops forever. If the input `AsyncVar<Optional<ClusterControllerFullInterface>>` is present, it writes the embedded `clientInterface` to the output `AsyncVar<Optional<ClusterInterface>>`; otherwise it clears the output. It then waits on `in->onChange()` and repeats.

Dependencies and integration: depends on `WorkerInterface.actor.h`, `AsyncVar`, `ClusterControllerFullInterface`, and `ClusterInterface`. It is a small glue actor used when worker or client code only needs the client subset of the cluster controller interface.

Risks and tests: output freshness depends on `onChange()` notifications and actor lifetime. Tests should verify transitions from absent to present, present to absent, replacement of a full interface, and cancellation without leaving dependent code with unexpected state.
