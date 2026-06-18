# sources/security-integrity/gocryptfs/internal/tlog/log.go

Purpose: Toggled logging support or tests for gocryptfs user-facing, debug, warning, fatal, color, and syslog output.

Important APIs and types: package `tlog`; types `toggledLogger`; functions/tests `JSONDump`, `trimNewline`, `Printf`, `Println`, `init`, `SwitchToSyslog`, `SwitchLoggerToSyslog`, `PrintMasterkeyReminder`; key imports `encoding/hex`, `encoding/json`, `fmt`, `log`, `log/syslog`, `os`, `golang.org/x/term`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/hex`, `encoding/json`, `fmt`, `log`, `log/syslog`, `os`, `golang.org/x/term`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
