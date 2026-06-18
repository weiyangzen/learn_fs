# sources/sync-backup/borg/src/borg/testsuite/archiver/_common_test.py

Purpose: verifies repository factory selection in `borg.archiver._common.get_repository` for legacy Borg v1 compatibility paths.

Important APIs/types/functions: `test_get_repository_ssh_v1_uses_legacy_remote` and `test_get_repository_local_v1_uses_legacy_repository` patch `borg.legacy.remote.LegacyRemoteRepository` and `borg.legacy.repository.LegacyRepository` respectively, then call `get_repository`.

Control flow: each test constructs a `MagicMock` location with `proto` set to `ssh` or `file`. With `v1_legacy=True`, SSH must instantiate `LegacyRemoteRepository`; local/file mode must bypass the borgstore branch and instantiate `LegacyRepository` with `location.path`.

State and persistence behavior: no repository is created; all effects are captured through mocks.

Dependencies and integration points: depends on the archiver common repository factory and the legacy repository import paths. It guards compatibility routing for commands that still access Borg 1 repositories.

Risks: import-path refactors or constructor signature changes will break these tests. The test is narrow and does not validate actual legacy repository behavior.

Test signals: confirms the correct class is selected and called with create/exclusive/lock options preserved.
