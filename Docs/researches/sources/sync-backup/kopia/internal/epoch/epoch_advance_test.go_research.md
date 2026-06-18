# sources/sync-backup/kopia/internal/epoch/epoch_advance_test.go

Purpose: table-driven verification of `shouldAdvance` epoch advancement criteria.

Important APIs/types/functions: `TestShouldAdvanceEpoch`, `DefaultParameters`, and `blob.Metadata` test cases.

Control flow: constructs metadata at fixed timestamps and lengths, including a generated slice large enough to meet the count threshold, then calls `shouldAdvance` with default thresholds and compares expected booleans.

State and persistence behavior: in-memory only.

Dependencies/integration: uses `time`, `blob`, and `testify/require`.

Risks/test signals: captures boundary behavior for duration and thresholds. It does not test negative/zero thresholds or unordered timestamps beyond a few cases.
