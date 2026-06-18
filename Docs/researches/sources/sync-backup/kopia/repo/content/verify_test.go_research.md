# sources/sync-backup/kopia/repo/content/verify_test.go

## Purpose
Exercises `WriteManager.VerifyContents` against healthy, missing, truncated, corrupted, deleted, regular-pack, and special-pack scenarios.

## Important APIs, Types, And Functions
Helpers `newTestingMapStorage` and `newTestWriteManager` create a test write manager with deterministic content format. Tests include `TestVerifyContents_NoMissingPacks`, `TestVerifyContentToPackMapping_EnsureCallbackIsCalled`, `TestVerifyContents_Deleted`, `TestVerifyContents_TruncatedPack`, `TestVerifyContents_CorruptedPack`, `TestVerifyContents_MissingPackP`, and `TestVerifyContentToPackMapping_MissingPackQ`.

## Control Flow
Tests write content, flush indexes/packs, then mutate underlying blob storage by deleting, truncating, or overwriting pack blobs. Verification is run with different options: deleted-content inclusion, `ContentIDRange` filters, 100% read sampling, and callback intervals. Assertions check either no error or `errMissingPacks` wrapping.

## State And Persistence
The tests use in-memory map storage and real content-manager flushes, so index entries and pack blobs are persisted in test storage. Mutations happen directly against blob storage to simulate corruption outside the content manager.

## Dependencies And Integration Points
Uses `blobtesting`, `epoch.DefaultParameters`, `format.ContentFormat`, `index.Version2`, `gather`, and `testlogging`. It tests the integration of content writes, index flushing, pack naming prefixes, and verification logic.

## Risks And Edge Cases
The tests distinguish non-prefixed regular `p` packs from prefixed special `q` packs using content ID ranges. They also verify that deleted contents only matter when `IncludeDeletedContents` is true. Callback tests use atomic counters so they remain valid if iterator parallelism is raised.

## Test Signals
Coverage is strong for repository-integrity outcomes. It does not test partial read percentages below 100%, concurrent mutation during verification, or logging contents.
