# sources/sync-backup/kopia/repo/content/content_index_recovery_test.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_index_recovery_test.go_research.md`.

Purpose: validates the pack-local recovery path used when repository index blobs are missing or damaged.

Important APIs and fixtures: the test uses `contentManagerSuite`, map-backed blob storage, `writeContentAndVerify`, `PackBlobIDPrefixes`, and `RecoverIndexFromPackBlob`. It explicitly deletes both legacy index blobs and epoch-style `x` blobs before reopening the manager.

Control flow and assertions: the test writes three contents, flushes them, removes all index blobs, closes and reopens the manager, and confirms all content lookups now return not found. It then iterates all pack blobs once with `commit=false`, expecting exactly three recovered entries but no visible content. A second scan uses `commit=true`, after which content reads work immediately. A final flush and reread confirm the recovered index entries can be persisted as normal index blobs.

State and persistence behavior: the test distinguishes transient recovery into `packIndexBuilder` from committed repository indexes. Recovery without commit is intentionally read-only. Recovery with commit rebuilds in-session index state but still requires `Flush` for durable repository-level indexes.

Dependencies and integration: exercises storage listing/deletion, pack blob prefixes, index blob prefixes, content manager reopen behavior, and seeded deterministic payload helpers.

Risks and coverage gaps: it validates the happy recovery path but not malformed postambles, incorrect lengths, corrupted local index ciphertext, or mixed valid and invalid packs. Those risks are handled by lower-level error returns rather than by this test.
