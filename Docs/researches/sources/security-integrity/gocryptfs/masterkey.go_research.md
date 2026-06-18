# sources/security-integrity/gocryptfs/masterkey.go

Purpose: Explicit master-key handling for recovery and test modes, including command-line, stdin, and all-zero key sources.

Important APIs and types: package `main`; functions/tests `unhexMasterKey`, `handleArgsMasterkey`; key imports `encoding/hex`, `os`, `strings`, `github.com/rfjakob/gocryptfs/v2/internal/cryptocore`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/hex`, `os`, `strings`, `github.com/rfjakob/gocryptfs/v2/internal/cryptocore`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
