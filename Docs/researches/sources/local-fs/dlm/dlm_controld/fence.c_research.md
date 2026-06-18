# File Research: sources/local-fs/dlm/dlm_controld/fence.c

## Purpose
Runs external fence/unfence agents and reports their asynchronous results for daemon-wide fencing coordination.

## Main Behavior
- `run_agent()` creates a pipe, forks, writes newline-separated agent arguments to child stdin, redirects child stdout/stderr to `/dev/null`, and `execlp()`s the configured agent.
- `fence_request()` builds fence arguments from `fence_config_agent_args()`, adds `fail_time=<walltime>`, launches the selected agent, logs request context, and returns the child pid.
- `fence_result()` polls a fence-agent pid with `waitpid(WNOHANG)`:
  - `-EAGAIN` means still running.
  - Exit status is returned as result.
  - Signal termination returns result `-1`.
- `unfence_node()` reads node fence config, runs all devices marked `unfence` with `action=on`, waits synchronously for each, and fails on the first run/wait/nonzero-exit error.

## Integration Points
- Used by `daemon_cpg.c` fencing work loop.
- Consumes parsed config from `fence_config.c`.
- Uses `reason_str()` for logging daemon CPG failure reason names.

## Risks and Notes
- Agent output is discarded, so diagnosis depends on daemon logs and agent exit status.
- Parent writes the entire argument buffer once and treats short writes as failure.
- `unfence_node()` is synchronous and can block daemon progress while agent commands run.
