<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go

Purpose: `health-monitor stop` subcommand that kills the health monitor associated with a specific Blobfuse2 process ID.

Important APIs/types/functions: global `blobfuse2Pid`, Cobra command `healthMonStop`, helper `getPid(blobfuse2Pid)`, helper `stop(pid)`, `ps aux`, regexp PID extraction, and `kill -9`.

Control flow: trim and validate `--pid`; scan `ps aux` output for a line containing `bfusemon` and `--pid=<blobfuse2Pid>`; extract the first numeric token as the monitor PID; call `kill -9 <pid>`; print success messages or return wrapped failure messages.

State/persistence behavior: mutates operating-system process state by forcibly killing the matched monitor. It does not update any Blobfuse config or pid file.

Dependencies/integration: registered under `healthMonCmd` and also attaches `healthMonStopAll`. It depends on Unix `ps` and `kill`, process command-line visibility, and the monitor binary name containing `bfusemon`.

Risks/test signals: matching by substring can select an unintended process, and the first-number regex assumes `ps aux` output starts with the PID after the user column. `kill -9` prevents graceful cleanup. Tests cover empty pid, nonexistent monitor pid, and direct kill failure for random PIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go -->
