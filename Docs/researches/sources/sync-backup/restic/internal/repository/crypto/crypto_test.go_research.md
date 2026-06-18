## sources/sync-backup/restic/internal/repository/crypto/crypto_test.go

Purpose: external-package tests for the public crypto API and buffer aliasing behavior.

Important tests/helpers: `TestEncryptDecrypt` checks multiple plaintext sizes. `TestSmallBuffer` verifies `Seal` grows insufficient destination capacity. `TestSameBuffer` checks decrypting into the same ciphertext buffer. Helpers `encrypt`, `decryptNewSliceAndCompare`, and `decryptAndCompare` validate append semantics. `TestAppendOpen` and `TestAppendSeal` cover nil, empty, small, large, and prefixed destinations. `TestLargeEncrypt` is gated by `testLargeCrypto`. Benchmarks measure encrypt/decrypt throughput.

Control flow and state: random data and nonces are generated for each case. Tests assert prefixes remain intact when appending to destination slices.

Dependencies and integration points: imports the package as `crypto`, so only exported behavior is tested. Uses restic random/test helpers and chunker size constants for optional large cases.

Risks and test signals: append/aliasing behavior is important because repository code reuses buffers for performance. Large encryption coverage is disabled by default, so chunker-maximum-size paths rely mostly on benchmarks/manual enablement.
