# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.h

Purpose: shared GoogleTest fixture for blob-store tests.

Important APIs/types/functions: `BlobStoreTest`, `BLOCKSIZE_BYTES`, `blobStore`, `loadBlob`, and `reset`.

Control flow: constructor is defined in the `.cpp`; helper `loadBlob` asserts `BlobStore::load` succeeds and moves out the loaded blob. `reset` consumes a blob ref to trigger destruction.

State and persistence behavior: owns a `unique_ref<BlobStore>` for each test. `reset` intentionally drops blob ownership so later loads validate store persistence.

Dependencies and integration points: includes GoogleTest and `blobstore/interface/BlobStore.h`; used by blob size/read/write/lifecycle tests.

Risks and test signals: `reset` relies on move-destruction side effects and can look like a no-op to readers. Helper asserts load success, so tests cannot inspect failure details through it.
