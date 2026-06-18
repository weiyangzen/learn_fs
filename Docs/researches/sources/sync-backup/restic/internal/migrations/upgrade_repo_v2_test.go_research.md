## sources/sync-backup/restic/internal/migrations/upgrade_repo_v2_test.go

Purpose: smoke test for the repository v2 migration.

Important tests: `TestUpgradeRepoV2` creates a version 1 repository, verifies the initial version, checks migration applicability, and calls `Apply`.

Control flow and state: the test uses `repository.TestRepositoryWithVersion` to build mutable repository state and applies the migration against it.

Dependencies and integration points: depends on the concrete repository package and context. It verifies that the migration connects to `repository.UpgradeRepo`.

Risks and test signals: the test does not assert the post-apply version or verify command-level migration reporting. It mainly catches registration/API drift and gross upgrade failures.
