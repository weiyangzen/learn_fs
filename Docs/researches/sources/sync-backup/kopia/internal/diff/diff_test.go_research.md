# sources/sync-backup/kopia/internal/diff/diff_test.go

Purpose: validates filesystem comparison output/stats and snapshot-selection helpers.

Important APIs/types/functions: fake `testFile`/`testDirectory`, `TestCompareEmptyDirectories`, `TestCompareIdenticalDirectories`, `TestCompareDifferentDirectories`, metadata-difference tests, `TestGetPrecedingSnapshot`, `TestGetTwoLatestSnapshots`, and helper manifest/object ID functions.

Control flow: tests build synthetic entries with names, modes, owners, mtimes, content, and object IDs, run `NewComparer`/`Compare`, assert output strings and `Stats`, then use an in-memory repository test environment to save snapshot manifests and query predecessor/latest behavior.

State and persistence behavior: comparer temp dirs are cleaned through `t.Cleanup`. Repository tests persist manifests in a test repository.

Dependencies/integration: uses `repotesting`, `snapshot.SaveSnapshot`, `content.IDFromHash`, `blake3`, and filesystem interfaces.

Risks/test signals: tests do not exercise external diff command execution or download error paths. They strongly cover object-ID metadata shortcuts and snapshot time sorting.
