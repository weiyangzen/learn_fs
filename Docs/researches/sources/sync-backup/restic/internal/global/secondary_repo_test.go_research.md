## sources/sync-backup/restic/internal/global/secondary_repo_test.go

Purpose: table-driven validation of `SecondaryRepoOptions.FillGlobalOpts`.

Important tests: valid cases check current `Repo`, current `RepositoryFile` with password file or command, legacy `LegacyRepo`, and legacy `LegacyRepositoryFile` with legacy password file or command. Invalid cases cover no repo, repo and repository-file conflicts, password file and command conflicts, missing password file, invalid command, and mixed current/legacy groups.

Control flow and state: the test changes into a temporary directory, writes a temporary password file, and uses an existing `Options` as source values to confirm secondary settings override only the intended fields.

Dependencies and integration points: depends on OS file APIs and restic test helpers. It verifies the compatibility layer used by copy/dump/restore-style commands that need a second repository.

Risks and test signals: it catches option migration regressions but does not exercise pflag deprecation/hidden marker behavior or environment-variable initialization from `AddFlags`.
