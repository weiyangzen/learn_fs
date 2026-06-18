# sources/security-integrity/gocryptfs/mount.go

Purpose: Mount lifecycle implementation that validates paths, initializes crypto/name transforms and FUSE frontends, configures go-fuse, handles daemonization, control sockets, idle unmount, and signal cleanup.

Important APIs and types: package `main`; types `AfterUnmounter`, `RootInoer`; functions/tests `doMount`, `idleMonitor`, `setOpenFileLimit`, `initFuseFrontend`, `initGoFuse`, `haveFusermount2`, `handleSigint`, `unmount`, `isReadOnlyFilesystem`; constants `checksDuringTimeoutPeriod`; key imports `bytes`, `log`, `log/syslog`, `math`, `os`, `os/exec`, `os/signal`, `path`, `path/filepath`, `runtime`, `runtime/debug`, `strings`, `syscall`, `time`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Security-sensitive policy is concentrated here: reverse mode requires AES-SIV, recursive/shadow mounts are rejected, force-owner implies allow_other, and read-only backing filesystems force read-only mounts. Control-socket behavior matters because path encryption/decryption is exposed over a local IPC surface and malformed paths must warn rather than panic. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `log`, `log/syslog`, `math`, `os`, `os/exec`, `os/signal`, `path`, `path/filepath`, `runtime`, `runtime/debug`, `strings`, `syscall`, `time`, `golang.org/x/crypto/chacha20poly1305`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
