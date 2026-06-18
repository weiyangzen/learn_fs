# sources/security-integrity/gocryptfs/main.go

Purpose: Main CLI entry point that parses options, loads/decrypts configuration, selects operations, and dispatches mount/init/passwd/info/fsck/speed behavior.

Important APIs and types: package `main`; functions/tests `loadConfig`, `changePassword`, `main`; key imports `log`, `os`, `path/filepath`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/contentenc`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/fido2`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/speed`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The CLI enforces exactly one operation flag, resolves config paths before loading secrets, and wipes password/master-key byte slices after use on a best-effort basis. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `log`, `os`, `path/filepath`, `runtime`, `strconv`, `strings`, `github.com/hanwen/go-fuse/v2/fuse`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/contentenc`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/fido2`, `github.com/rfjakob/gocryptfs/v2/internal/readpassword`, `github.com/rfjakob/gocryptfs/v2/internal/speed`, `github.com/rfjakob/gocryptfs/v2/internal/tlog`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
