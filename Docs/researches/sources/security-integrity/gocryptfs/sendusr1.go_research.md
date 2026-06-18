# sources/security-integrity/gocryptfs/sendusr1.go

Purpose: Top-level gocryptfs support source in this mapped research subset.

Important APIs and types: package `main`; functions/tests `sendUsr1`; key imports `os`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `syscall`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
