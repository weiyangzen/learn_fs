# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobSizeTest.cpp

Purpose: blob size and resize semantics tests.

Important APIs/types/functions: `BlobSizeTest`, `BlobSizeDataTest`, `Blob::size`, `resize`, `write`, `read`, `blockId`, and `loadBlob`.

Control flow: tests grow, shrink, resize-to-self, reload after size changes, and write at/after/over end. Data tests verify zero-fill and data retention when growing, shrinking, and regrowing.

State and persistence behavior: validates that size metadata persists across destruction/reload and that truncated regions are not resurrected after regrowth.

Dependencies and integration points: inherits `BlobStoreTest`, uses `DataFixture` for random data and `cpputils::Data` zero buffers.

Risks and test signals: strong coverage for resize invariants and sparse growth zeroing. Large sizes are 5-10 MiB here, so 64-bit overflow coverage is delegated to `BigBlobsTest`.
