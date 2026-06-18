# sources/sync-backup/restic/cmd/restic/cmd_prune_integration_test.go

Purpose: broad integration coverage for prune behavior on normal, damaged, and edge-case repositories.

Important APIs/types/functions: `testRunPrune`; `testRunPruneMustFail`; `testRunPruneOutput`; `createPrunableRepo`; `testRunForgetJSON`; `testPrune`; `TestPruneWithDamagedRepository`; `TestEdgeCaseRepos`; `testEdgeCaseRepo`; `TestPruneRepackSmallerThanSmoke`; `TestPruneJSON`.

Control flow and state: tests build repositories with forgotten snapshots to create unused data, run prune with multiple policies, then run check. Edge cases load fixture repositories with missing indexes, missing blobs, unused missing data, unreferenced data, obsolete indexes, mixed packs, and duplicate blobs. JSON test captures `repository.PruneStats`.

Dependencies and integration points: uses backend list-once hooks, forget/check helpers, fixture tar repositories, and repository error values such as `ErrPacksMissing`.

Risks: fixture expectations encode repository invariants. Some tests deliberately manipulate packs and rely on local backend behavior.

Test signals: high-value coverage for prune safety and repair boundaries, including cases prune must not repair.
