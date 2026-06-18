# sources/user-network-fs/rclone/backend/archive/archive_test.go

Purpose: Runs rclone's standard filesystem integration test suite against the archive backend.

Important APIs/types/functions: Defines `unimplementableFsMethods` and `unimplementableObjectMethods` expected not to work. `TestIntegration` runs against `-remote` if provided. `TestLocal` and `TestMemory` configure archive remotes wrapping a temp local directory or `:memory:` and run `fstests.Run` with `QuickTestOK`.

Control flow: Tests skip remote-specific cases depending on `fstest.RemoteName`. Extra config items create archive remotes for local and memory tests.

State and persistence: Uses temp local directory or in-memory backend. Standard fstests create/remove test objects in those remotes.

Dependencies and integration points: Imports local and memory backends, `fstest`, and `fstests`. Validates archive backend against rclone's generic Fs contract while acknowledging unsupported methods.

Risks: Since archive contents are read-only but wrapper delegates writes to underlying remotes, some generic tests may not cover actual archive file contents. Unimplementable lists must stay in sync with backend capabilities.

Test signals: Broad interface-compatibility signal for archive as a wrapper backend.
