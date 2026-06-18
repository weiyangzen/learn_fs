# sources/user-network-fs/bazil-fuse/mount.go

Purpose: `mount.go` contains shared helper logic for platform mount implementations, specifically line-based logging for mount helper stdout/stderr.

Important APIs, types, and functions: `neverIgnoreLine` always returns false. `lineLogger(wg, prefix, ignore, r)` scans an `io.ReadCloser`, logs non-ignored lines with a prefix, logs scanner errors, and calls `wg.Done` when finished.

Control flow: Platform mount functions start helper commands, obtain stdout/stderr pipes, and launch `lineLogger` goroutines. Ignore callbacks can suppress known noisy lines or capture structured errors while allowing other helper output through logging.

State and persistence behavior: No durable state. It coordinates goroutine completion through a `sync.WaitGroup` and writes to the process logger.

Dependencies and integration points: Used by `mount_linux.go` and `mount_freebsd.go`. Depends on `bufio.Scanner`, `io`, `log`, and `sync`.

Risks: `bufio.Scanner` has a default token size limit; extremely long helper lines could produce scanner errors. Logging helper output can expose environment-specific details but is valuable for mount diagnostics.

Test signals: Mount error path tests in `serve_test.go` and mount option tests indirectly exercise this logging path when helpers fail.
