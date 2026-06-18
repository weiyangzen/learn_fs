# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/replicas/ReplicaVerifier.java

Purpose: `ReplicaVerifier` is the common interface for per-replica block checks used by `ReplicasVerify`.

Important APIs and types: It declares `verifyBlock(DatanodeDetails, OmKeyLocationInfo)` and `getType()`.

Control flow and state: Implementations perform the actual work. The interface defines no state.

Dependencies and integration points: Implemented by block existence, checksum, and container state verifiers. `ReplicasVerify` stores a list of these implementations and serializes each result under its type.

Risks and test signals: Adding a verifier requires stable `getType` strings for JSON and summary counters. Tests should verify each implementation conforms to the pass/completed semantics.
