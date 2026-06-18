## sources/user-network-fs/gcsfuse/internal/perf/cpu.go

### Purpose
`cpu.go` installs a signal-driven CPU profiling loop for operational debugging.

### Important APIs, Types, And Functions
`HandleCPUProfileSignals` creates a local `profileOnce(duration, path)` helper, registers for `SIGUSR1`, and writes profiles under `/tmp/cpu-<nanotime>.pprof`.

### Control Flow
On each SIGUSR1, it creates a timestamped profile file, starts `pprof.StartCPUProfile`, sleeps for 30 seconds, stops profiling, closes the file, and logs success or error. The signal loop runs forever.

### State, Persistence, And Dependencies
State is the process-wide CPU profiler and signal subscription. Persistent artifacts are pprof files in `/tmp`. Dependencies include `os/signal`, `syscall`, `runtime/pprof`, `time`, and logger.

### Integration Points
This is intended to be run in a goroutine by the main process so operators can trigger CPU profiles without restarting a mount.

### Risks
`StartCPUProfile` fails if another CPU profile is already active. The handler blocks for the profile duration per signal, so repeated signals queue in a size-one channel and may be dropped by signal semantics. Files are written to `/tmp` without cleanup.

### Test Signals
No tests are present, likely because signal/profiler globals are awkward. Manual signals and profile-file creation are the practical validation.
