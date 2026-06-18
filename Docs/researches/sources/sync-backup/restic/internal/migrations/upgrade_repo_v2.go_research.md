## sources/sync-backup/restic/internal/migrations/upgrade_repo_v2.go

Purpose: migration implementation that upgrades a repository from format version 1 to version 2.

Important APIs/types: `init` registers `&UpgradeRepoV2{}`. `UpgradeRepoV2` implements `Migration`: `Name` returns `upgrade_repo_v2`; `Desc` describes the repository v2 upgrade; `Check` returns true only for repositories whose config version is exactly 1 and otherwise returns a reason; `RepoCheck` returns true; `Apply` calls `repository.UpgradeRepo`.

Control flow and state: `Apply` type-asserts `restic.Repository` to `*repository.Repository`, so it mutates only the concrete repository implementation. The persistent state change is delegated to `repository.UpgradeRepo`, which updates repository format metadata.

Dependencies and integration points: integrates migration registry, `restic.Repository.Config`, and repository upgrade code. Commands can use `Check` to report non-applicability before applying.

Risks and test signals: the concrete type assertion can panic if called with a non-standard repository implementation. The check only distinguishes version 1 from other versions and assumes future versions are already upgraded. `TestUpgradeRepoV2` covers applicability and successful apply on a v1 test repo.
