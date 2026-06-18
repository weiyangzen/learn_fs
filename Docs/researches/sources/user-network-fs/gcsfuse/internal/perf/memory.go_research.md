## sources/user-network-fs/gcsfuse/internal/perf/memory.go

### Purpose
`memory.go` installs a signal-driven heap profile dump path for debugging memory usage.

### Important APIs, Types, And Functions
Constants define `KiB` and `MiB`. `HandleMemoryProfileSignals` creates `profileOnce(path)`, listens for `SIGUSR2`, logs current heap allocation, and writes `/tmp/mem-<nanotime>.pprof`.

### Control Flow
Each signal triggers `runtime.GC`, creates a profile file, writes the heap profile with `pprof.Lookup("heap").WriteTo`, reads current memory stats for logging, and reports success/failure. The loop runs indefinitely.

### State, Persistence, And Dependencies
State is process signal registration and runtime heap profiler state. Persistent artifacts are heap profile files in `/tmp`. Dependencies include `runtime`, `runtime/pprof`, `os/signal`, `syscall`, `time`, and logger.

### Integration Points
This complements CPU profiling and can be enabled by the main daemon for live mount diagnostics.

### Risks
Forcing GC changes process timing and memory behavior while profiling. Like CPU profiles, files accumulate in `/tmp`. The signal loop blocks while writing the profile.

### Test Signals
No direct tests. Validation is usually via sending SIGUSR2 and loading the generated pprof file.
