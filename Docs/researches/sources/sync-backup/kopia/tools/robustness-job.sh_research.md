# sources/sync-backup/kopia/tools/robustness-job.sh

Purpose: orchestrates Kopia randomized robustness testing by building the Kopia binary, embedding repo metadata, optionally sourcing test runtime configuration, and invoking the robustness Make target.

Control flow/APIs: required args are robustness repo directory, Kopia repo directory, test duration, timeout, and repo path prefix. It logs environment, optionally inspects fio data storage, builds `kopia`, collects git metadata for both repos, builds ldflags for `tests/robustness/engine`, chooses `robustness-server-tests` when `ENGINE_MODE=SERVER` otherwise `robustness-tests`, sources `$TEST_RC` if it names a file, then runs `make -C`.

State/persistence: writes the Kopia executable, may source arbitrary shell from `TEST_RC`, and delegates repository/test state creation to the robustness tests under the provided path prefix.

Dependencies/integration: bash, Go, Git, Make, optional fio/Docker, S3-related environment, and the Kopia robustness test repo. It is CI or cron-style validation glue.

Risks/test signals: `source ${TEST_RC}` is unquoted and intentionally executes external code. Complex `TEST_FLAGS` quoting can be fragile. Long-running randomized tests may be flaky if storage credentials, fio paths, or timeouts are wrong. Test success/failure is the direct output of the Make target.
