# sources/sync-backup/kopia/internal/server/api_paths_test.go

Purpose: tests path resolution API behavior.

Important APIs/types/functions: `TestPathsAPI`.

Control flow: starts a test server, authenticates, calls the path resolution endpoint, and asserts resolved output matches local path rules.

State and persistence behavior: no repository mutation beyond test setup.

Dependencies and integration points: covers request routing, CSRF, and `ospath` integration.

Risks and test signals: OS-dependent path rules may require conditional expectations on Windows versus Unix.
