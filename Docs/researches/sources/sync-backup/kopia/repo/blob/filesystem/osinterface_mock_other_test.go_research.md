# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_other_test.go

Purpose: non-Unix test implementation detail for `mockOS.Stat`.

Important APIs/types/functions: platform-specific `(*mockOS).Stat`.

Control flow: provides the mock stat behavior for platforms that do not use the Unix-specific mock implementation. It returns configured stat results/errors used by filesystem storage tests.

State and persistence behavior: uses in-memory mock OS state; no real files are required for these paths.

Dependencies/integration points: selected by build tags to keep mock behavior compatible with platform-specific file info/error types. Risks are low but platform divergence can hide test gaps if Unix and non-Unix mocks behave differently. Its test signal is indirect through `filesystem_storage_test.go` on non-Unix builds.
