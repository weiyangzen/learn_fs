# sources/sync-backup/kopia/repo/manifest/manifest_entry_test.go

Purpose: tests manifest metadata latest-selection and label deduplication.

Important APIs/types/functions: `TestPickLatestID`, `TestDedupeEntryMetadataByLabel`, `PickLatestID`, and `DedupeEntryMetadataByLabel`.

Control flow: cases construct metadata with different mod times, IDs, and labels, then assert selected IDs or deduped result order.

State/persistence behavior: no persisted state; tests pure metadata helpers.

Dependencies/integration: uses Go time values and assertion helpers.

Risks/test signals: protects deterministic tie-breaking and ordering relied on by callers handling duplicate manifests.
