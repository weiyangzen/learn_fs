<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_bsd.go -->
# sources/user-network-fs/rclone/cmd/siginfo_bsd.go

Source read: complete file, 23 lines, 434 bytes, sha256 `55f63c183ae1854e505e3102e678dec4a2103fb84b104009cf78a8952b4ba2be`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/siginfo_bsd.go_research.md`.

## Purpose
Adds SIGINFO handling on BSD-like platforms to print global transfer statistics.

## Important APIs, types, and functions
`SigInfoHandler` creates a signal channel, registers for `syscall.SIGINFO`, and starts a goroutine that prints `accounting.GlobalStats()` for each signal.

## Control flow
Called from command startup on supported platforms; signal delivery triggers asynchronous stats output.

## State and persistence behavior
State is one signal channel and goroutine in the process. No persistent state.

## Dependencies and integration points
Depends on build tags for Darwin/BSD variants, `os/signal`, `syscall`, `fs.Printf`, and accounting stats.

## Risks and edge cases
Multiple registrations would create multiple goroutines if called more than once. Output is asynchronous with ongoing transfers.

## Test signals
Platform build and manual signal behavior are the test signal; no local unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_bsd.go -->
