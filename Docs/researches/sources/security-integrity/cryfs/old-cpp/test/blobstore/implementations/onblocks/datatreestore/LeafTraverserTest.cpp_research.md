# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/LeafTraverserTest.cpp

Purpose: unit tests for `LeafTraverser`, verifying which leaves are visited or created across tree depths and ranges.

Important APIs/types/functions: `LeafTraverserTest`, `TraversorMock`, `LeafTraverser::traverseAndUpdateRoot`, `LeafHandle`, `EXPECT_TRAVERSE_LEAF`, `EXPECT_CREATE_LEAF`, `CreateThreeLevel`, and `CreateFourLevel`.

Control flow: constructs known tree shapes, sets gmock expectations for leaf callbacks, flushes/loads the tree, invokes `traverseAndUpdateRoot`, and checks whether root ownership changes in read-only versus mutating traversals.

State and persistence behavior: traverser may update root and create new leaves when growing ranges. Read-only traversal must leave the root pointer unchanged; mutating traversal may replace root.

Dependencies and integration points: inherits `DataTreeTest`, uses gmock matchers, `DataNodeStore`, `DataInnerNode`, `DataLeafNode`, and `DataTreeStore`.

Risks and test signals: extensive coverage of first/middle/last ranges in two-, three-, and four-level trees. Tests encode exact leaf index mapping and right-border semantics, which are core to safe data tree updates.
