# sources/sync-backup/kopia/repo/content/verify.go

## Purpose
Verifies repository content index entries against physical pack blobs. It detects missing packs, truncated packs, and optionally corrupted/unreadable contents by sampling actual content reads.

## Important APIs, Types, And Functions
`VerifyOptions` controls content ID range, read percentage, deleted-content inclusion, iterator parallelism, and progress callback interval. `VerifyProgressStats` reports success/error counts. `WriteManager.VerifyContents` delegates to `contentVerifier.verifyContents`. Internal verification functions are `verify`, `verifyContentImpl`, and `logCountMap`.

## Control Flow
Verification first builds a map of all existing blob metadata with `blob.ReadBlobMap`. It then iterates repository contents using `WriteManager.IterateContents`, honoring range, parallelism, and deleted-content options. Each content entry is checked for pack existence and bounds; if configured, it probabilistically calls `GetContent` to validate decryption/hash/integrity. Counters and per-pack error maps are updated atomically, progress callbacks fire every configured interval, and a wrapped corruption error is returned when any content error count is nonzero.

## State And Persistence
The verifier is transient and stores an in-memory blob metadata map, atomic counters, and counter maps keyed by pack blob ID. It does not mutate repository state.

## Dependencies And Integration Points
Depends on `blob`, `internal/stats.CountersMap`, `logging`, `WriteManager.IterateContents`, and `WriteManager.GetContent`. It is a repository maintenance/integrity operation that relies on index metadata and pack layout correctness.

## Risks And Edge Cases
The existing blob map is a snapshot; concurrent repository writes/deletes could make verification report stale missing/truncated errors. `math/rand` sampling is non-cryptographic and nondeterministic. When `ContentReadPercentage` is zero, corruption inside otherwise correctly sized packs is not detected. Error reporting intentionally reuses `errMissingPacks` for all verification failures, including truncation and corruption.

## Test Signals
`verify_test.go` covers healthy packs, callback invocation on success and failure, deleted-content inclusion/exclusion, truncated packs, corrupted packs with 100% reads, and regular/special pack ranges.
