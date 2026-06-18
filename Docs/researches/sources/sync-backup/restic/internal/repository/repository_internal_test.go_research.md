
# sources/sync-backup/restic/internal/repository/repository_internal_test.go

Purpose: tests internal repository helpers that are not exposed through the external repository package API, especially cached-pack ordering, index load benchmarks, streaming pack reads, and write-time verification.

Important tests include `TestSortCachedPacksFirst`, `BenchmarkLoadIndex`, `TestStreamPack`, `TestBlobVerification`, `TestUnpackedVerification`, and `TestStreamPackFallback`. `buildPackfileWithoutHeader` constructs deterministic encrypted blob sequences for streaming tests. `TestStreamPack` verifies range coalescing, sorting, split behavior for distant blobs, short read retry behavior, and invalid inputs such as duplicate/overlapping entries or too-short blobs. Verification tests damage plaintext, compressed bytes, and ciphertext to check error classification.

State is mostly synthetic pack bytes and test repositories. Integration points include zstd, crypto keys, backend load callbacks, `streamPack`, `verifyCiphertext`, `verifyUnpacked`, and cache handling. Risks covered include corrupted data detection, fallback to alternate blob copies, overlapping range defense, excessive backend reads, and verification bypass regressions.
