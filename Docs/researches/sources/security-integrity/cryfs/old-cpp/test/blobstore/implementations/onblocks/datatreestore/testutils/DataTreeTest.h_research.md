# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.h

Purpose: declaration of reusable data-tree test fixture and helper API.

Important APIs/types/functions: `DataTreeTest`, `BLOCKSIZE_BYTES`, tree construction helpers, node loading helpers, fixture fields `_blockStore`, `blockStore`, `_nodeStore`, `nodeStore`, `treeStore`, validation helpers, and `CHECK_DEPTH`.

Control flow: header exposes helpers used by data tree performance and traverser tests; implementation is in `DataTreeTest.cpp`.

State and persistence behavior: fixture owns a mock block store and data node store, while `treeStore` owns the node store after construction. Raw observer pointers allow tests to inspect counters and layout.

Dependencies and integration points: includes GoogleTest, `FakeBlockStore`, `MockBlockStore`, data node/tree store headers, and block IDs.

Risks and test signals: raw observer pointers depend on ownership staying valid inside `treeStore`. Copy/assign is disabled to avoid duplicating ownership-heavy fixture state.
