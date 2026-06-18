# sources/sync-backup/kopia/repo/maintenance/content_rewrite_test.go

Purpose: integration tests content rewrite selection, dry-run behavior, prefix filtering, and stats.

Important APIs/types/functions: `TestContentRewrite`, `RewriteContentsOptions`, `maintenance.RewriteContents`, direct write sessions, and pack blob listings.

Control flow: each case creates separate write sessions to force multiple `p` and `q` pack blobs, runs rewrite inside a direct write session, lists pack blobs before/after, and compares blob-count deltas and `RewriteContentsStats`.

State/persistence behavior: creates real temporary repository content and pack blobs; rewrite cases persist new packs while dry-run cases do not.

Dependencies/integration: uses `repotesting`, object writers with default and custom prefixes, UUID payloads, blob listing, and `SafetyNone`.

Risks/test signals: verifies no rewrite for single-pack cases and correct prefix scoping. Expected sizes are format-sensitive and could need updates if pack encoding changes.
