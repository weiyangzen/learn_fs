# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.cpp

Purpose: implementation of the blob-store test fixture constructor.

Important APIs/types/functions: `BlobStoreTest::BLOCKSIZE_BYTES`, `BlobStoreTest::BlobStoreTest`, `RustBlobStore`, and `new_locking_inmemory_blobstore`.

Control flow: initializes `blobStore` with a Rust bridge in-memory blob store using the fixture block size.

State and persistence behavior: each test fixture gets an isolated in-memory blob store; persistence is limited to the lifetime of that fixture instance.

Dependencies and integration points: includes `RustBlobStore` and cpputils GCC compatibility header. A commented line shows a previous/onblocks fake-store implementation path.

Risks and test signals: tests under `onblocks` names now exercise Rust bridge blob store behavior, so directory naming may mislead. In-memory backing avoids disk flakiness but may not expose on-disk persistence issues.
