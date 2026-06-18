# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobReadWriteTest.cpp

Purpose: read/write behavior tests for blobs, including empty reads, zero-byte writes, partial overwrites, full-range reads, and persistence after reloading.

Important APIs/types/functions: `BlobReadWriteTest`, `BlobReadWriteDataTest`, `DataRange`, `readBlob`, `EXPECT_DATA_READS_AS`, `EXPECT_DATA_IS_ZEROES_OUTSIDE_OF`, `Blob::tryRead`, `read`, `readAll`, `write`, `resize`, and `blockId`.

Control flow: fixture creates random data and a blob. Basic tests cover empty and zero-size behavior. Parameterized tests run many offset/count/blob-size combinations across single-leaf and large multi-leaf blobs.

State and persistence behavior: writes modify blob content and may grow size; reload tests destruct and reload by `BlockId` to verify persisted data and zero-filled untouched ranges.

Dependencies and integration points: inherits `BlobStoreTest`, uses `DataNodeLayout` to choose leaf boundaries, and relies on `DataFixture` for deterministic content.

Risks and test signals: broad coverage of boundary ranges and partial updates. It expects `read` beyond blob size to throw while `tryRead` returns zero; implementation changes must preserve that API split.
