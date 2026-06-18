# sources/test-tools/syzkaller/pkg/covermerger/mocks/FileVersProvider.go

Purpose: generated testify mock for the `covermerger.FileVersProvider` interface.

Important APIs/types/functions: `NewFileVersProvider`, `FileVersProvider`, `GetFileVersions`, and typed call helper `FileVersProvider_GetFileVersions_Call`.

Control flow: constructor registers expectation assertion cleanup. `GetFileVersions` passes the target file and variadic repo commits to `mock.Called`, then returns mocked `covermerger.FileVersions` and error values. Helper methods support `Run`, `Return`, and `RunAndReturn`.

State and persistence: mock expectations only.

Dependencies and integration: used by tests that need to isolate merge logic from real Git/web providers. Depends on `covermerger` and testify mock.

Risks: variadic arguments are packed as a slice for mock matching, so expectations must be configured accordingly. Generated code should not be edited manually.

Test signals: infrastructure for focused covermerger tests; this subset uses a hand-written provider in `covermerger_test.go` instead of this mock.
