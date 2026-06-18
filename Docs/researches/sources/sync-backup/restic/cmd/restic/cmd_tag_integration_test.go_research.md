# sources/sync-backup/restic/cmd/restic/cmd_tag_integration_test.go

Purpose: integration coverage for snapshot tag mutation lifecycle.

Important APIs/types/functions: `testRunTag`; `TestTag`.

Control flow and state: creates a repository and backup, verifies no initial tags/original ID, then runs tag set, add, remove, combined add/remove-all, and set-empty operations. After each mutation it runs check and reloads newest snapshot through `testRunSnapshots`, asserting tags and `Original` ID remain tied to the first snapshot.

Dependencies and integration points: uses `data.TagLists`, backup/check/snapshots helpers, and test assertions.

Risks: assumes newest snapshot after tag rewrite is the modified one. Does not cover JSON output or invalid option combinations.

Test signals: validates user-visible tag semantics and snapshot lineage preservation.
