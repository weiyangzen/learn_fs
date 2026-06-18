# sources/sync-backup/kopia/snapshot/restore/shallow_helper_test.go

Purpose: boundary test for shallow placeholder cleanup around platform filename length limits.

Important APIs/types/functions: `TestSafeRemoveAll`, `MaxFilenameLength`, `localfs.ShallowEntrySuffix`, and `SafeRemoveAll`.

Control flow: the test creates a temp directory, iterates filename lengths around the maximum minus suffix space, tries to create the placeholder sidecar, calls `SafeRemoveAll` on the unsuffixed path, and verifies any actually-created sidecar is removed.

State and persistence: uses temporary files only. Some attempted writes are expected to fail because the filename is too long; that is not a test failure.

Dependencies and integration points: validates the contract shared by `long_paths_*` implementations and restore placeholder cleanup.

Risks and test signals: the loop depends on the platform-specific `MaxFilenameLength` constant and filesystem behavior. The key signal is no cleanup error and no leftover sidecar when creation succeeded.
