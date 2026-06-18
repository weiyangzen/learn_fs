# sources/user-network-fs/rclone/cmd/mount/test/seekers.go

Purpose: standalone stress tool that launches many concurrent random-seek readers over files in a directory tree, intended to exercise mount concurrency and cache behavior.

Important APIs/state: flags `--size`, `--n`, `--tries`, `--maxsleep`, `--stats`; `findFiles` walks a directory; `seekTest` opens a random file, optionally sleeps, then performs random one-byte reads. A shared stats goroutine prints runtime memory stats if enabled.

Control flow: `main` discovers files, starts optional stats ticker, then launches `tries` goroutines staggered by one second. Completion is tracked by a channel.

State/persistence: read-only file access, stdout/stderr logging. Dependencies include `filepath.Walk`, random, runtime metrics. Risks include using global `math/rand` concurrently, noisy timing, and test-only fatal process exits. No automated tests.
