<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/test/vars.go -->
# sources/sync-backup/restic/internal/test/vars.go

## Purpose
Centralizes environment-controlled test configuration.

## Important APIs and Control Flow
Package variables read `RESTIC_TEST_PASSWORD`, cleanup/tempdir flags, integration/FUSE toggles, SFTP path, benchmark directory, and disallow-skip behavior via `getStringVar`/`getBoolVar`. Control flow parses environment values at package initialization, with boolean parsing/fatal behavior handled by helper functions.

## State, Persistence, Dependencies, and Integration
State is process-global test configuration for the test binary. It integrates with repository, backend, FUSE, and integration tests.

## Risks and Test Signals
Risks are surprising global state from environment variables and tests changing behavior across machines. The signal is operational rather than unit-tested: many tests rely on these variables.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/test/vars.go -->
