
# sources/sync-backup/restic/internal/repository/lock_file_unix.go

Purpose: provides Unix process-liveness detection for stale repository locks. It is compiled for non-Windows platforms.

The file installs a process-wide SIGHUP listener in `init` via `sync.Once`, logging received SIGHUP signals so restic can probe its own processes without terminating. `lockHandle.processExists` calls `os.FindProcess`, sends `syscall.SIGHUP`, releases the process handle, and treats signal failure as evidence that the process is gone or unreachable.

State behavior is external to the repository: this only queries local OS process state to support `lockHandle.stale`. Integration points are `lock_file.go` stale detection and the debug logger. Risks include platform differences around `FindProcess` semantics, permission failures being treated as stale, and process-ID reuse; the host-name check in `stale` limits probes to locks from the current host. Tests exercise this path indirectly through stale-lock tests using current and fake PIDs.
