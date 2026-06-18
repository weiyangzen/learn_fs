# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_test.go

Purpose: provides the central mock OS and mock file types for filesystem storage tests.

Important APIs/types/functions: `mockOS`, `errNonRetriable`, methods for `Open`, `Rename`, `ReadDir`, `Remove`, `Chtimes`, `Chown`, `CreateNewFile`, `Mkdir`, `MkdirAll`, `Geteuid`, plus failure file types `readFailureFile`, `writeFailureFile`, `syncFailureFile`, `writeCloseFailureFile`, and `mockDirEntryInfoError`.

Control flow: mock methods either delegate to configured functions/errors or simulate filesystem behavior needed by tests. Failure file wrappers inject read/write/sync/close errors. Directory-entry wrappers inject `Info` failures.

State and persistence behavior: all state is in mock fields and temporary test files. It enables deterministic testing of retry and cleanup paths that are hard to force with the real OS.

Dependencies/integration points: used by filesystem storage tests and sync tests. Risks include mock behavior diverging from real OS semantics, especially path/link error classification and file modes. The breadth of tests using this mock gives strong signals for `fsImpl` error paths, but it should not be treated as proof of crash durability.
