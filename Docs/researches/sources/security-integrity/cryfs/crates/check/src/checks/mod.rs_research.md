# sources/security-integrity/cryfs/crates/check/src/checks/mod.rs

Purpose: This module defines the common filesystem-checking interface and the `AllChecks` fan-out aggregator used by the runner. It centralizes how blob and node observations are delivered to individual checks.

Important APIs and flow: `BlobToProcess` wraps readable `FsBlob` references or unreadable `BlobId`s. `NodeToProcess` wraps readable `DataNode`s or unreadable `BlockId`s. `FilesystemCheck` defines callbacks for reachable blobs, repeated reachable blobs, reachable nodes, unreachable nodes, and finalization. `AllChecks` owns mutex-protected `CheckUnreferencedNodes`, `CheckParentPointers`, `CheckBlobsReadable`, plus `additional_errors`.

State and persistence: Each check accumulates in-memory reference state while the runner traverses concurrently. Mutexes make `AllChecks` safe to call from multiple spawned tasks, but the checks themselves remain sequential critical sections.

Dependencies and integration: This module imports CryFS blobstore/blockstore/fsblobstore types and reexports internal check modules. The runner calls only `AllChecks` methods, keeping traversal separate from corruption-specific logic.

Risks and test signals: Adding a new check requires updating each fan-out method manually; TODO comments call out the risk of forgetting a member. The top-level TODO list documents many future integrity checks that are not yet implemented, including tree balance, cycles, type mismatches, directory-entry validity, zeroed unused space, and integrity block ids.
