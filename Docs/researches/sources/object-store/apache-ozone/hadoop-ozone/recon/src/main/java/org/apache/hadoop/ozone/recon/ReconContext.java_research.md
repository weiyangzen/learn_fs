# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/ReconContext.java

## Purpose
`ReconContext` is a singleton runtime health and identity context shared by Recon modules. It tracks cluster ID, node thread prefix, health status, and user-facing error metadata.

## Important APIs, Types, And Functions
The class exposes `isHealthy`, `updateHealthStatus`, `threadNamePrefix`, error metadata getters, `updateErrors`, cluster ID accessors, and the `ErrorCode` enum. Error codes cover topology, certificates, internal errors, snapshot failures, and upgrade failures.

## Control Flow
Construction derives Recon node details from `ReconUtils`, stores the thread prefix, and initializes maps from each `ErrorCode` to messages and impacted UI areas. Health updates atomically replace the boolean value and log the transition.

## State And Persistence
State is in-memory only: `clusterId`, `AtomicBoolean isHealthy`, synchronized error list, and error metadata maps. Nothing is persisted.

## Dependencies And Integration Points
It is injected into `ReconServer`, upgrade handling, health endpoints, node managers, and OM provider code. It depends on `OzoneConfiguration` and `ReconUtils`.

## Risks
The error list can accumulate duplicates and has no removal API. `updateHealthStatus` accepts an `AtomicBoolean` but copies only the current value, which may be surprising. Maps are mutable and exposed directly.

## Test Signals
Tests should verify initialization of error metadata, thread prefix derivation, health transitions, error recording, and cluster ID storage.
