# sources/storage-engines/foundationdb/fdbrpc/AsyncFileEncrypted.cpp

Purpose: encrypted `IAsyncFile` wrapper for append-only writes and read-only reads. It encrypts data in fixed-size blocks using FoundationDB stream cipher support and derives per-block IVs from filename-derived salt plus block number.

Important APIs and types: `AsyncFileEncryptedImpl` contains coroutine helpers `getFirstBlockIV`, `readBlock`, `read`, `write`, `sync`, and `zeroRange`. `AsyncFileEncrypted` exposes `read`, `write`, `zeroRange`, `truncate`, `sync`, `flush`, `size`, `getFilename`, zero-copy stubs, `debugFD`, `getIV`, and `writeLastBlockToFile`.

Control flow: read mode lazily obtains file size, clamps requested length at EOF, reads full encrypted blocks, decrypts each block, and copies requested slices. append-only write mode asserts writes occur exactly at current EOF, encrypts chunks into `writeBuffer`, writes full blocks as they fill, and reinitializes the encryptor for the next block. Sync writes the final partial block then syncs the underlying file.

State and persistence behavior: durable bytes are encrypted in the underlying file. Runtime state includes mode, current block, offset within block, write buffer, encryptor, cached file size, encryption block size, and first block IV. Truncate forwards to the underlying file only in append mode.

Dependencies and integration points: depends on `AsyncFileEncrypted.h`, Flow `StreamCipher`, global cipher key, `xxhash`, arenas, and Flow unit-test macros.

Risks: random writes are unsupported and enforced with assertions. `size` is read-only only. `readZeroCopy`/`releaseZeroCopy` throw `io_error`. IV salt strips directory and extension, so files with the same basename stem share first-block salt.

Test signals: embedded `TEST_CASE("fdbrpc/AsyncFileEncrypted")` writes random data in random chunks, syncs, reads in random chunks, and asserts plaintext round trip in simulation.
