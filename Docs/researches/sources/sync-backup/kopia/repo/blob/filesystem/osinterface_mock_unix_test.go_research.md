# sources/sync-backup/kopia/repo/blob/filesystem/osinterface_mock_unix_test.go

Purpose: Unix-specific mock `Stat` behavior for filesystem storage tests.

Important APIs/types/functions: `(*mockOS).Stat`, using Unix-aware file info/stat behavior.

Control flow: selected on Unix-like builds, this method supplies stat results/errors to tests that need platform-specific metadata or errno handling.

State and persistence behavior: test-only mock state. No external persistence is involved.

Dependencies/integration points: complements `osinterface_mock_test.go` and Unix-specific stale error tests. Risks include platform-specific assumptions that may differ across Linux/macOS/BSD. Its effectiveness is indirect through the filesystem test suite.
