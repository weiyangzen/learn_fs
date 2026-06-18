# sources/security-integrity/gocryptfs/tests/defaults/main_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestMain`, `Test1980Tar`, `TestOpenTruncateRead`, `TestWORead`, `TestXfs124`, `TestWrite0200File`, `TestMvWarnings`, `TestMvWarningSymlink`, `TestCpWarnings`, `TestSeekData`, `TestMd5sumMaintainers`, `TestMaxlen`, `TestFsync`, `TestForceOwner`, `TestSeekDir`; key imports `bytes`, `fmt`, `io`, `os`, `os/exec`, `path/filepath`, `runtime`, `strings`, `sync`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `fmt`, `io`, `os`, `os/exec`, `path/filepath`, `runtime`, `strings`, `sync`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
