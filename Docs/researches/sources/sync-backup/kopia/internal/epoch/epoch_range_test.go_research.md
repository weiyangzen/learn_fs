# sources/sync-backup/kopia/internal/epoch/epoch_range_test.go

Purpose: validates longest contiguous range checkpoint selection and tie-breaking.

Important APIs/types/functions: `TestLongestRangeCheckpoint` and `newEpochRangeMetadataForTesting`.

Control flow: constructs reusable range metadata for ranges such as 0-9, 0-29, 10-59, etc., passes different combinations to `findLongestRangeCheckpoint`, and compares exact pointer slices.

State and persistence behavior: in-memory only; `Blobs` are irrelevant for these tests.

Dependencies/integration: uses `testify/require`.

Risks/test signals: good coverage for chain continuity and shorter-chain tie preference. It does not cover invalid ranges where `MinEpoch > MaxEpoch` or negative epochs.
