# Research: sources/sync-backup/syncthing/test/override_test.go

## sources/sync-backup/syncthing/test/override_test.go

Purpose: integration test for send-only folder override behavior.

Important APIs/functions: `TestOverride`, config mutation to `FolderTypeSendOnly`, REST POST `/rest/db/override?folder=default`, and `rc.AwaitSync`.

Control flow: rewrites h1 default folder to send-only, creates initial data, syncs to h2, edits a file on h2, rescans h2 and waits for index propagation, posts override on h1, waits for sync, then verifies h1 did not accept h2 changes and h2 was reverted. A longer ignore-related override test is present but commented out.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes, and temporarily h1 config.

Dependencies and integration: config loader, REST override endpoint, send-only model logic. Risks include fixed sleep for index propagation, config restore on failure, and behavior around ignored files left untested. Test signal is file content after override.
