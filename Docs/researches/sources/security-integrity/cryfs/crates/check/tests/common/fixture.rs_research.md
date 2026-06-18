## sources/security-integrity/cryfs/crates/check/tests/common/fixture.rs

Purpose: end-to-end filesystem fixture for `cryfs_check` integration tests. It creates a real CryFS config, encrypted/integrity/locking blockstore stack over an in-memory blockstore, a root directory blob, and focused APIs for corrupting or removing blobs and nodes.

Important APIs and types: `FilesystemFixture` owns root blob id, shared blockstore, loaded config, and tempdir. Constructors are `new` and `new_with_some_blobs`. Store accessors include `update_blockstore`, `update_nodestore`, `update_blobstore`, and `update_fsblobstore`. Mutation helpers corrupt blocks, blob header fields, parent pointers, root/inner/leaf nodes, and multi-node subtrees. Result structs (`RemoveInnerNodeResult`, `CorruptInnerNodeResult`, `RemoveLeafNodeResult`, `CorruptLeafNodeResult`, `RemoveSomeNodesResult`, `CorruptSomeNodesResult`) carry expected-reference metadata.

Control flow and state: `new` creates temp config with fixed password, initializes root dir, and all later updates reopen the relevant store stack through `setup_blockstore_stack_dyn`. `run_cryfs_check(self)` consumes the fixture and calls `cryfs_check::check_filesystem`, preserving the shared blockstore but letting tempdir live until after the check.

Dependencies and integration: integrates `cryfs_cli_utils` blockstore setup, config/local state, blockstore integrity settings, fsblobstore, blobstore, nodestore, and common entry helpers.

Risks and test signals: corruption helpers intentionally violate integrity and graph invariants while preserving enough metadata to assert exact checker errors. The fixture panics on unexpected integrity violations in normal setup, so tests distinguish fixture failures from checker findings.
