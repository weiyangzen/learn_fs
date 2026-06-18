# sources/security-integrity/gocryptfs/internal/syscallcompat/thread_credentials_linux_32.go

Purpose: Portable and security-conscious syscall wrapper code or tests for dirfd-relative operations, no-follow behavior, credentials, xattrs, directory reads, rename flags, EINTR handling, and platform differences.

Important APIs and types: build tags: (linux && 386) || (linux && arm); package `syscallcompat`; functions/tests `Setreuid`, `Setregid`, `setgroups`; key imports `unsafe`, `golang.org/x/sys/unix`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem centralizes syscall details so higher-level FUSE code can use safer defaults such as `O_CLOEXEC`, no-follow lookup, EINTR retry, and platform-specific fallbacks. Credential changes are especially sensitive: Linux uses raw per-thread syscalls and locked OS threads to avoid process-wide UID/GID changes.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `unsafe`, `golang.org/x/sys/unix`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
