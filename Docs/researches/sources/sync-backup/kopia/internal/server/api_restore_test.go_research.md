# sources/sync-backup/kopia/internal/server/api_restore_test.go

Purpose: integration-tests restoring snapshots through the API.

Important APIs/types/functions: `TestRestoreSnapshots`.

Control flow: creates test snapshot data, starts server/client, invokes restore API, waits for task completion, and verifies restored filesystem output.

State and persistence behavior: temporary repository plus restored local files in test directories.

Dependencies and integration points: covers snapshot creation, restore engine, task manager, and API client behavior.

Risks and test signals: should catch regressions in object selection and task completion but may not cover all overwrite/error modes.
