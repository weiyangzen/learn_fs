# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobStoreTest.cpp

Purpose: basic blob-store lifecycle tests for unique IDs and deletion.

Important APIs/types/functions: `BlobStoreTest`, `BlobStore::create`, `load`, `remove`, `Blob::blockId`, and `reset`.

Control flow: creates blobs, compares IDs, removes blobs directly, by key, and after reload, then verifies load returns empty.

State and persistence behavior: deletion must remove persisted blob state such that subsequent loads by `BlockId` fail.

Dependencies and integration points: uses `BlobStoreTest` fixture, Boost optional helpers, and blockstore `BlockId`.

Risks and test signals: covers simple lifecycle behavior only; concurrent open references, double deletion, and remove error cases are not covered here.
