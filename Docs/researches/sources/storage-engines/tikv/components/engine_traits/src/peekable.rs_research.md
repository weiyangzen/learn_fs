# sources/storage-engines/tikv/components/engine_traits/src/peekable.rs

Purpose: Defines point-read operations for engines and snapshots.

Important APIs and control flow: `Peekable` associates a `DbVector` result type and requires option-aware default-CF and CF-specific gets. Default helpers use default read options, and protobuf helpers decode returned bytes into default message instances.

State, persistence, and dependencies: Reads observe persistent or snapshot state but do not mutate it. Dependencies include `ReadOptions`, `DbVector`, and protobuf.

Integration points, risks, and test signals: Used by nearly all key-value read paths. Risks include CF mismatch, protobuf decode failures, fill-cache option propagation gaps, and snapshot consistency requirements. Shared tests cover default-CF equivalence, writes followed by reads, snapshots, and read consistency during later writes.
