<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go

Purpose: unit tests for health-monitor option validation, bfusemon CLI construction, invalid start conditions, and stop subcommands.

Important APIs/types/functions: `configHmonTest`, `hmonTestSuite`, `generateRandomPID`, `validateHMonOptions`, `buildCliParamForMonitor`, `executeCommandC`, `stop`, and constants from `tools/health-monitor/common`.

Control flow: setup installs a silent debug logger. Tests validate empty pid/config messages, construct monitor options with all disable-list variants plus an invalid option and assert the generated CLI length, run the hidden command with empty or nonexistent config, run it with a valid config but expect external `bfusemon` startup failure, and exercise stop-all, empty pid, nonexistent monitor pid, and direct kill failure.

State/persistence behavior: writes a temporary config file for the startup-failure case and resets health-monitor CLI flags after most tests. It uses random PIDs intended not to correspond to live processes.

Dependencies/integration: depends on command helpers, file-cache option structs, common logger, Unix process commands used by stop helpers, and absence of a matching `bfusemon` process for negative tests.

Risks/test signals: random PID generation uses `os.FindProcess`, which does not reliably prove nonexistence on Unix; tests are still mostly negative-path checks. If `bfusemon` is installed and accepts the generated config, the expected failure test could change behavior. The suite is useful for parameter translation and error contracts, not for monitoring correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go -->
