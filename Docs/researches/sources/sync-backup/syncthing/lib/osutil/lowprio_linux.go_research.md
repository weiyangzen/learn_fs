## sources/sync-backup/syncthing/lib/osutil/lowprio_linux.go

Purpose: Linux-specific lowering of process CPU priority, with process-group handling to affect all threads.

Important API: `SetLowPriority` checks current kernel nice value, moves the process into its own process group when needed, then calls `syscall.Setpriority` for the process group.

Control flow and state: if current priority is already low enough it returns nil. Otherwise it ensures process group leadership through `Getpgid` and `Setpgid`, then sets priority to the kernel-translated value for user nice 9.

Dependencies and integration points: called during startup when Syncthing is configured to run with lower CPU/IO priority.

Risks: process group changes can fail under supervisors or permission constraints. Linux nice values use inverted kernel representation, making constants subtle. Errors are returned for callers to log/handle.

Test signals: no direct tests in this subset.
