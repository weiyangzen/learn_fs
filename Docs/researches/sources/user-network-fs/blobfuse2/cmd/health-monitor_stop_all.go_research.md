<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go

Purpose: `health-monitor stop all` subcommand that terminates all running health monitor binaries.

Important APIs/types/functions: Cobra command `healthMonStopAll`, helper `stopAll`, `exec.Command("killall", hmcommon.BfuseMon)`, and `hmcommon.BfuseMon`.

Control flow: run `killall <bfusemon-binary-name>`, return a wrapped error if the command fails, and print a success message otherwise.

State/persistence behavior: mutates OS process state by killing all monitor processes with the configured binary name. It does not inspect mount ownership or update monitor state files.

Dependencies/integration: depends on Unix `killall` behavior and the shared health monitor binary-name constant. It is registered as a child of `health-monitor stop`.

Risks/test signals: broad process-name termination may affect monitors for unrelated Blobfuse2 mounts or tests. It returns an error when no matching process exists on systems where `killall` exits nonzero; the included test expects this failure path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go -->
