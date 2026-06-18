# Research: sources/sync-backup/syncthing/test/reconnect_test.go

## sources/sync-backup/syncthing/test/reconnect_test.go

Purpose: verifies transfers survive sender or receiver restarts during throttled synchronization.

Important APIs/functions: `TestReconnectReceiverDuringTransfer`, `TestReconnectSenderDuringTransfer`, and shared `testReconnectDuringTransfer`.

Control flow: generates files, starts h1/h2, sets receiver send/receive rate limits and LAN limiting through config API, resumes both, polls receiver model progress, restarts the selected side whenever progress crosses another 10 percent, then resets rate limits, stops both, compares directories, and verifies remote in-sync state.

State and persistence: mutates `s1`, `s2`, h1/h2 indexes and h2 runtime config.

Dependencies and integration: connection manager, block transfer resume/retry, config REST API, rate limiting. Risks include timing and progress thresholds, restart races, and failure to reset config after test failure. Test signal is final directory equality and remote in-sync checks.
