## sources/security-integrity/cryfs/crates/check/tests/node_referenced_multiple_times.rs

Purpose: tests data-tree nodes referenced from multiple parents, including leaf nodes, non-root inner nodes, and blob root nodes referenced as children inside other blobs.

Important APIs and functions: helper mutations replace a child pointer in one parent with an existing node from another tree: `remove_leaf_and_replace_in_parent_with_another_existing_leaf`, `remove_inner_node_and_replace_in_parent_with_another_existing_inner_node`, and `remove_inner_node_and_replace_in_parent_with_root_node`. The `rstest_reuse` template parameterizes source/target blob combinations across file, directory, and symlink blobs.

Control flow and state: helpers select deterministic nodes, update a parent’s child pointer, remove the original subtree to avoid unrelated duplicate/missing noise, and return parent ids for expected references. Tests run the checker, filter a documented set of acceptable flakiness-caused errors from potentially unreadable modified directory blobs, and assert the exact `NodeReferencedMultipleTimesError`.

Dependencies and integration: uses low-level `BlockId` operations, `RemoveResult`, node search helpers, `MaybeBlobReferenceWithId`, and checker reference enums. It stress-tests the checker’s ability to attribute duplicate data nodes to different reachable blobs and depths.

Risks and test signals: comments document disabled cases involving self-referential directories, child/parent directory references, and a flaky directory case where blob ids may still decode. The existing tests still cover core duplicate-node detection across different blob types and root/non-root roles.
