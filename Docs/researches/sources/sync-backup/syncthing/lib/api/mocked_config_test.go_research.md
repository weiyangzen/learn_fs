# sources/sync-backup/syncthing/lib/api/mocked_config_test.go

Purpose: Test helper for constructing config wrapper mocks with successful default mutation behavior.

Important APIs/types/functions: `newMockedConfig` returns `*mocks.Wrapper` with `Modify`, `RemoveFolder`, and `RemoveDevice` preconfigured to return `noopWaiter` and nil errors. `noopWaiter.Wait` is a no-op.

Control flow: Straight-line mock setup.

State and persistence behavior: No real persistence; tests that require save behavior use real config wrappers elsewhere.

Dependencies and integration points: Used heavily by `api_test.go` to start API services without a real config file.

Risks: Because it defaults modifications to success without mutating state, tests using it can miss real config state transitions unless they assert through explicit mock returns.

Test signals: Supports API service tests by removing config persistence as a variable.
