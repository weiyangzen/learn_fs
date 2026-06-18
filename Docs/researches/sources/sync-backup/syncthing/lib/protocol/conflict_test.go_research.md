## sources/sync-backup/syncthing/lib/protocol/conflict_test.go

Purpose: tests conflict winner selection for `FileInfo`.

Important test: `TestWinsConflict` constructs file infos with versions, modification times, and invalid flags to assert `WinsConflict` behavior.

Control flow and state: table/simple assertions compare pairs and expected winners.

Dependencies and integration points: validates conflict resolution used by model global/local reconciliation and request conflict tests.

Risks: narrow coverage; broader conflict behavior also depends on `InConflictWith` and model-level conflict file creation.

Test signals: focused unit coverage for tie-break rules.
