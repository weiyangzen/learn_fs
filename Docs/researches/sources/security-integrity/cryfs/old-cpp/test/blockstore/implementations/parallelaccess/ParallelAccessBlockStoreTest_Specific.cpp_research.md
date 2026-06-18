# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/parallelaccess/ParallelAccessBlockStoreTest_Specific.cpp

Purpose: Tests `ParallelAccessBlockStore::physicalBlockSizeFromVirtualBlockSize` boundary behavior. It verifies conversion from virtual to physical block sizes across zero, positive, and negative boundaries.

Important APIs and types: Uses `ParallelAccessBlockStore` and `FakeBlockStore`, though the tested API is the static physical-size conversion helper. GoogleTest assertions check exact expected integer results.

Control flow: Independent test cases call the conversion helper with representative virtual sizes and compare returned physical sizes. The fixture class is minimal.

State and persistence behavior: No block store is persisted or mutated; the tested behavior is pure arithmetic/configuration logic.

Dependencies and integration points: Integrates the parallel-access blockstore implementation with its fake lower store include path, ensuring the test target compiles against the production API.

Risks: Boundary conversion bugs can corrupt block layout decisions or produce invalid lower-layer accesses. The test is focused on explicit examples rather than exhaustive property coverage.

Test signals: Exact results for zero physical, zero virtual, negative boundary cases, and ordinary positive conversion.
