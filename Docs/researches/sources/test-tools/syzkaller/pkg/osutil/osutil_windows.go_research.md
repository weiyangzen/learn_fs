# sources/test-tools/syzkaller/pkg/osutil/osutil_windows.go

Purpose: Windows-specific process helper shims.

Important APIs: `HandleInterrupts` is a no-op. `ProcessExitStatus` extracts the exit status from `syscall.WaitStatus`.

Control flow and state: No persistent state; functions are simple platform-specific implementations.

Dependencies and integration: Satisfies osutil API for Windows builds.

Risks: No interrupt handling means graceful shutdown-by-signal behavior differs from Unix. Exit status extraction assumes the `ProcessState.Sys()` type.

Test signals: No direct tests in this shard.
