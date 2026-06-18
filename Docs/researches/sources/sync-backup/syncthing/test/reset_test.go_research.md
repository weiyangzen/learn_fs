# Research: sources/sync-backup/syncthing/test/reset_test.go

## sources/sync-backup/syncthing/test/reset_test.go

Purpose: integration test for REST-triggered database reset of one folder and all folders.

Important APIs/functions: `TestReset`, helper `createFiles`, REST POST `/rest/system/reset?folder=...` and `/rest/system/reset`.

Control flow: creates files, starts h1, confirms local model count, deletes data while preserving `.stfolder`, verifies invalid-folder reset fails, resets default folder and waits for Syncthing to exit, restarts and checks zero files, recreates files and rescans, resets all indexes, waits for exit again, restarts, and verifies file count is restored by scanning.

State and persistence: deletes/recreates `s1`, `.stfolder`, and h1 indexes; process exits are expected side effects.

Dependencies and integration: REST reset endpoint, database lifecycle, startup scanning. Risks include EOF handling during restart, timeout sensitivity, and marker preservation. Test signal is process stop and `Model.LocalFiles` counts.
