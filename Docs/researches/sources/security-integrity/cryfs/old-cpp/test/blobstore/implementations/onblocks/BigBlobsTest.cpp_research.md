# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BigBlobsTest.cpp

Purpose: regression tests ensuring blob operations work above the 4 GiB boundary and do not use 32-bit size arithmetic.

Important APIs/types/functions: `BigBlobsTest`, constants `SMALL_BLOB_SIZE`, `LARGE_BLOB_SIZE`, `Blob::resize`, `write`, `read`, `flush`, `blockId`, `BlobStore::load`, and `remove`.

Control flow: creates an in-memory Rust blob store, resizes across the 4 GiB threshold, writes sparse ranges near/after that threshold, reloads blobs, and compares generated fixture data.

State and persistence behavior: blob size and sparse data are persisted through the blob store and validated after reload in the resize test.

Dependencies and integration points: uses Rust bridge `RustBlobStore`, compressing in-memory store factory, `DataFixture`, and `cpputils::destruct`.

Risks and test signals: excellent signal for 64-bit offsets, but tests can be expensive in memory/time if backing implementation materializes sparse data. TODO notes `Blob::readAll` above 4 GiB remains untested.
