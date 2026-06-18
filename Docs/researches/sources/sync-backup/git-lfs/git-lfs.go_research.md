<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs.go -->
# sources/sync-backup/git-lfs/git-lfs.go

## Research

This is the Git LFS executable entrypoint. `main` registers for interrupt and kill signals, starts a goroutine that runs `commands.Cleanup`, reports the signal, and exits with `128 + signal number` when possible. Normal execution calls `commands.Run`, then `commands.Cleanup`, and exits with the returned code.

State is limited to the signal channel and process exit path. Integration is with the full `commands` package lifecycle, translation, and OS signal handling. Risks include `os.Kill` not being catchable on Unix, cleanup racing with command execution, repeated signals triggering repeated cleanup attempts, and exit code portability across platforms. Tests would need process-level integration rather than unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs.go -->
