# sources/sync-backup/kopia/repo/manifest/manifest_entry.go

Purpose: defines public manifest metadata and helpers for selecting or deduplicating metadata entries.

Important APIs/types/functions: `EntryMetadata`, `DedupeEntryMetadataByLabel`, `PickLatestID`, and `isLaterThan`.

Control flow: dedupe groups entries by a label value and keeps the latest entry per value, then sorts results by mod time and ID. `PickLatestID` scans entries and returns the ID with latest mod time, using ID tie-breaks.

State/persistence behavior: metadata mirrors persisted manifest entries but this file only manipulates in-memory slices.

Dependencies/integration: used by maintenance params and higher-level snapshot/manifest lookups where concurrent duplicate labels can exist.

Risks/test signals: entries missing the dedupe label collapse under the empty string key. Tie-breaking by lexicographic ID is arbitrary but deterministic. Tests cover latest picking and label dedupe.
