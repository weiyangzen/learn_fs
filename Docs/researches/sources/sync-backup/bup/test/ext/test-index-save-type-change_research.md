## sources/sync-backup/bup/test/ext/test-index-save-type-change

Purpose: regression test for saving when an indexed path changes file type.

Important control flow: indexes a dead symlink, replaces it with a regular file without reindexing, then verifies `bup save` fails and the saved folder listing is empty.

State and dependencies: temp repo, filesystem path type mutation, `bup index`, `bup save`, and `bup ls`.

Risks covered: save must not trust stale index type information and accidentally archive wrong content.
