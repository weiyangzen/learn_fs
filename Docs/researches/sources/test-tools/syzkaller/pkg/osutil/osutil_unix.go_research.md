# sources/test-tools/syzkaller/pkg/osutil/osutil_unix.go

Purpose: Unix-family helpers for process temp directories, interrupt handling, and long pipes.

Important APIs: `ProcessTempDir`, `HandleInterrupts`, and `LongPipe`; internal `cleanupTempDir`.

Control flow: `ProcessTempDir` takes an exclusive flock on `instance-lock`, scans `instance-0` to `instance-999`, tries to create a directory, cleans stale directories whose `.pid` process no longer exists, writes the current pid, and returns the path. `HandleInterrupts` closes a shutdown channel on first SIGINT/SIGTERM, prints escalating messages on second/third signal, and exits on third. `LongPipe` creates an `os.Pipe` and calls platform `prolongPipe`.

State and persistence: Creates instance directories and `.pid` files under a caller-provided root. Signal handling mutates process behavior.

Dependencies and integration: Used for VM/process workspace allocation and graceful manager shutdown on Unix platforms.

Risks: Stale cleanup depends on pid reuse and `.pid` integrity. The 1000-instance limit is fixed. Signal handler assumes it owns shutdown channel closure and can exit the process.

Test signals: `fileutil_test.go` stress-tests concurrent `ProcessTempDir` allocation and stale cleanup.
