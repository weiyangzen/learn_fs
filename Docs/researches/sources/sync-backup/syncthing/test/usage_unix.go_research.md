# sources/sync-backup/syncthing/test/usage_unix.go

Purpose: Unix-like implementation of benchmark resource reporting for Syncthing integration benchmarks, compiled under `integration && benchmark && !windows`.

Important APIs/functions: `printUsage(name string, proc *os.ProcessState, total int64)` extracts `*syscall.Rusage` from `ProcessState.SysUsage`, logs user CPU, system CPU, and maximum resident set size.

Control flow: if the process state exposes `syscall.Rusage`, it computes `mib := total / 1024 / 1024`, logs `Utime.Nano()/mib` and `Stime.Nano()/mib`, adjusts Darwin RSS units from bytes to KiB, then logs `Maxrss`.

State/persistence: no persistent state. It only reads OS-provided process usage after a child exits and writes benchmark log output.

Dependencies/integration: integrates with `transfer-bench_test.go` after `sender.Stop()` and `receiver.Stop()`. Uses Syncthing `build.IsDarwin` to normalize platform RSS semantics.

Risks: CPU-per-MiB division assumes `total >= 1 MiB`; current benchmark callers satisfy this, but generic reuse may not. Linux and Darwin report `Maxrss` in different units, and the code handles only the documented Darwin special case.

Test signals: benchmark output should include `Receiver` and `Sender` `Utime`, `Stime`, and `MaxRSS` lines on supported Unix platforms.
