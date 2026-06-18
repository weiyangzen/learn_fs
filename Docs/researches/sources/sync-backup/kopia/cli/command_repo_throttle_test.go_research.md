<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_throttle_test.go -->
# sources/sync-backup/kopia/cli/command_repo_throttle_test.go

Purpose: integration test for repository throttling get/set behavior, unlimited values, invalid negatives, and JSON output.

Important APIs/types/functions: `TestRepoThrottle`, `throttling.Limits`, `testenv.NewCLITest`, `repo throttle get`, `repo throttle set`, and `testutil.MustParseJSONLines`.

Control flow: the test creates a filesystem repository, verifies all throttle limits start unlimited, sets download/upload speeds, request rates, and concurrent read/write limits, checks negative values fail, verifies formatted text output, resets two values to `unlimited`, and parses JSON output into `throttling.Limits`.

State/persistence behavior: mutates the repository throttler limits in the active direct repository and reads them back through the same CLI layer.

Dependencies/integration: depends on common throttle flag helpers, repository throttler persistence, unit formatting, and JSON output. Risks/test signals: text expectations are exact, including spacing and `GB/s` formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_repo_throttle_test.go -->
