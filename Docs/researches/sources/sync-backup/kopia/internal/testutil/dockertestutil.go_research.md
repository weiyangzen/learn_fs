<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/dockertestutil.go -->
# sources/sync-backup/kopia/internal/testutil/dockertestutil.go

- Purpose: Provides Docker execution helpers for tests that depend on containers.
- Important APIs/types/functions: `RunDockerAndGetOutputOrSkip`, `runDockerAndGetOutputOrSkip`, `RunContainerAndKillOnCloseOrSkip`, `GetContainerMappedPortAddress`.
- Control flow: Runs `docker` commands with test logging context, skips locally on failure but fails in CI, registers cleanup to kill containers, and parses mapped ports/`DOCKER_HOST`.
- State and persistence: External Docker containers are started and killed through test cleanup.
- Dependencies and integration points: Integrates `exec.CommandContext`, `testlogging`, `testing`, and Docker CLI behavior.
- Risks and edge cases: Docker availability changes test outcome; cleanup uses a context without cancellation because `t.Context()` is canceled during cleanup.
- Test signals: Utility file; no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/testutil/dockertestutil.go -->
