# sources/sync-backup/kopia/repo/manifest/committed_manifest_manager.go

Purpose: manages committed manifest entries stored in `m`-prefixed repository contents, including loading, merging, writing, and compaction.

Important APIs/types/functions: `committedManifestManager`, `getCommittedEntryOrNil`, `findCommittedEntries`, `commitEntries`, `writeEntriesLocked`, `loadCommittedContentsLocked`, `loadManifestContentsLocked`, `compactLocked`, `mergeEntryLocked`, `ensureInitializedLocked`, `loadManifestContent`, and `newCommittedManager`.

Control flow: reads are guarded by a mutex and call `ensureInitializedLocked`, which reloads manifest contents when content-manager revision changes. Loading iterates manifest contents in parallel, decodes gzip-compressed JSON, merges latest entries by mod time/ID, and removes entries marked deleted. Writes encode entries into a gzip JSON manifest content. Compaction writes the current live set while index flushing is disabled, deletes old manifest contents, and flushes when auto-compaction triggers.

State/persistence behavior: maintains cached committed entries, committed content IDs, and last content revision in memory; persists manifest batches as repository content and deletes superseded manifest contents during compaction.

Dependencies/integration: depends on content manager, gather buffers, gzip/json encoding, content index prefix iteration, and serialized manifest decoder.

Risks/test signals: compaction must be atomic with index flush disabled or manifests can be lost. Malformed content normally prevents loading unless `KOPIA_IGNORE_MALFORMED_MANIFEST_CONTENTS` is set. Tests cover corrupted content, compaction, read-only auto-compaction behavior, and reloads.
