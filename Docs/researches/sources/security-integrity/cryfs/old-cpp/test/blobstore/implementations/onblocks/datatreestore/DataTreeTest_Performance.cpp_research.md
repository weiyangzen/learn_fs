# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/DataTreeTest_Performance.cpp

Purpose: performance-contract tests for `DataTree` traversal, deletion, and resizing, measured by mock block-store load/create/remove/write/resize counters.

Important APIs/types/functions: `DataTreeTest_Performance`, `TraverseByWriting`, `TraverseByReading`, `DataTreeStore::remove`, `DataTree::writeBytes`, `readBytes`, `resizeNumBytes`, and `MockBlockStore` counters.

Control flow: builds specific two-level/three-level/four-level tree shapes, resets block-store counters, performs an operation, and asserts exact counts of loaded, created, removed, written, and resized blocks.

State and persistence behavior: tree structure persists as data nodes in a mock block store. Tests ensure operations mutate only necessary tree nodes and avoid loading leaves when overwriting full ranges.

Dependencies and integration points: inherits `DataTreeTest`, relies on `DataNodeLayout` limits, `MockBlockStore`, and data tree store implementation.

Risks and test signals: very high signal for algorithmic regressions and accidental I/O amplification. Exact counter expectations are brittle when legitimate internal traversal strategies change.
