<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github_test.go -->
# sources/sync-backup/restic/internal/selfupdate/github_test.go

## Purpose
Tests GitHub request construction for self-update.

## Important APIs and Control Flow
`TestNewGitHubRequest` verifies method, URL, Accept header, and optional Authorization header when `GITHUB_ACCESS_TOKEN` is set or empty. Control flow uses subtests and `t.Setenv` to isolate environment state.

## State, Persistence, Dependencies, and Integration
No persistent state. Dependencies include `net/http` constants and shared test assertions.

## Risks and Test Signals
The test catches auth/header regressions but does not mock full GitHub release or asset download responses.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/github_test.go -->
