# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.cpp

Purpose: implementation of reusable data-tree test fixture helpers for constructing, loading, and validating synthetic tree shapes.

Important APIs/types/functions: `DataTreeTest::DataTreeTest`, `CreateLeaf`, `CreateInner`, `CreateLeafOnlyTree`, `FillNode`, `FillNodeTwoLevel`, `CreateFullTwoLevel`, `CreateFullThreeLevel`, `LoadInnerNode`, `LoadLeafNode`, size-specific tree builders, `EXPECT_IS_*`, and `CHECK_DEPTH`.

Control flow: fixture wires a `MockBlockStore` into a `DataNodeStore` and `DataTreeStore`. Helpers create leaf/inner nodes, fill children to layout limits, load and cast nodes, and recursively validate depth.

State and persistence behavior: all constructed nodes are persisted in the mock block store and addressed by `BlockId`; helper methods may resize last leaves to model partial trees.

Dependencies and integration points: uses `DataNodeStore`, `DataTreeStore`, `MockBlockStore`, `dynamic_pointer_move`, and `cpputils::unique_ref`.

Risks and test signals: centralizes tree topology setup for many tests. Some helpers pass temporary-created node pointers into `CreateInner`; correctness depends on node creation persisting before temporary ownership is destroyed.
