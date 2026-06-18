## sources/user-network-fs/gcsfuse/benchmarks/stat_files/main.go

Purpose: Benchmark repeated `Stat` calls across many anonymous files.

Important APIs/types/functions: flags `--dir`, `--num_files`, `--duration`; `closeAll`; `createFiles(dir, numFiles)` creates files concurrently with errgroup, atomic counter, and `fsutil.AnonymousFile`; `run()` validates flags, creates files, loops stat calls, and reports Hz.

Control flow: create up to 128 worker goroutines, each creates anonymous files until count reached and sends handles through a channel; collect file handles; then repeatedly call `Stat` round-robin until duration expires.

State and persistence: holds open anonymous temp files and closes them at defer. Files are anonymous via fsutil, reducing cleanup burden.

Dependencies and integration points: uses `golang.org/x/sync/errgroup`, old `golang.org/x/net/context`, `github.com/jacobsa/fuse/fsutil`, and internal formatting.

Risks: `for range parallelism` requires a Go version supporting integer range. Error message wraps create failure as `ListBackups`, likely copy/paste noise. Very high parallel file creation may stress test filesystems. `Stat` count modulo assumes file creation returned at least one file, ensured by positive `num_files`.

Test signals: benchmark output; no unit tests.
