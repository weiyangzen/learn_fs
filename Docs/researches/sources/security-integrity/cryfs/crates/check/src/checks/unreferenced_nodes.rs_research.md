# sources/security-integrity/cryfs/crates/check/src/checks/unreferenced_nodes.rs

Purpose: This module checks node graph consistency: existing nodes should be referenced, referenced nodes should exist, unreadable nodes should be reported, and nodes should not be referenced multiple times. It handles reachable and unreachable node sets separately so dangling blob trees can be reported at their roots.

Important APIs and flow: `UnreferencedNodesReferenceChecker` wraps `ReferenceChecker<BlockId, SeenInfo, ReferencedAs>` plus `CheckResult`. Readable nodes are marked seen with leaf/inner depth and inner-node children are marked referenced. Unreadable nodes are marked seen as unreadable and add an assertion for `NodeUnreadableError`. Readable directory blobs mark child blob root nodes referenced. Finalization emits `NodeMissingError`, `NodeUnreadableError`, `NodeReferencedMultipleTimesError`, and `NodeUnreferencedError`.

State and persistence: Two in-memory checkers are kept: one for nodes reachable from the filesystem root and one for unreachable nodes found by scanning all blocks. The reachable checker is seeded with the root blob's root node reference.

Dependencies and integration: It integrates with `FilesystemCheck`, `BlobToProcess`, `NodeToProcess`, `DataNode`, fsblobstore directory entries, and node/blob reference model types. The runner feeds reachable node references with full blob context, while `check_all_unreachable_nodes` passes unreachable nodes without root reachability context.

Risks and test signals: The module has TODOs around unreachable blob processing and invariant panics. It assumes the runner sends reachable nodes consistently; unexpected `NodeUnreferenced` in the reachable checker is treated as an algorithm bug. It is central to integration tests such as missing blob scenarios.
