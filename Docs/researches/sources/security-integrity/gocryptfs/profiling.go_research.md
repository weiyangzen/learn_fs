# sources/security-integrity/gocryptfs/profiling.go

Purpose: CPU, memory, and execution-trace profile setup used by CLI profiling flags.

Important APIs and types: package `main`; functions/tests `setupCpuprofile`, `setupMemprofile`, `setupTrace`; key imports `os`, `runtime/pprof`, `runtime/trace`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `runtime/pprof`, `runtime/trace`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
