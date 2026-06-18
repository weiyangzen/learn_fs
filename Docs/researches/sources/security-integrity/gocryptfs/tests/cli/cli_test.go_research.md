# sources/security-integrity/gocryptfs/tests/cli/cli_test.go

Purpose: Integration or regression test file in the cli tests suite.

Important APIs and types: package `cli`; functions/tests `TestMain`, `TestInit`, `TestInitFilePerms`, `TestInitDevRandom`, `TestInitAessiv`, `TestInitReverse`, `TestInitMasterkey`, `testPasswd`, `TestPasswd`, `cp`, `TestPasswdMasterkey`, `TestPasswdMasterkeyStdin`, `TestPasswdReverse`, `TestPasswdScryptn`, `TestInitConfig`, `TestRo`, `TestNonempty`, `TestNofail`, `TestShadows`, `TestMountPasswordIncorrect`, `TestMountPasswordEmpty`, `TestPasswdPasswordIncorrect`, `TestMountBackground`, `TestMultipleOperationFlags`, `TestNoexec`, `TestMissingOArg`, `TestExcludeForward`, `TestConfigPipe`, `TestComma`, `TestIdle`, `TestNotIdle`, `TestSymlinkedCipherdir`, `TestBadname`, `TestPassfile`, `TestPassfileX2`; key imports `bytes`, `encoding/hex`, `errors`, `fmt`, `os`, `os/exec`, `strconv`, `strings`, `sync`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Control-socket behavior matters because path encryption/decryption is exposed over a local IPC surface and malformed paths must warn rather than panic. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `bytes`, `encoding/hex`, `errors`, `fmt`, `os`, `os/exec`, `strconv`, `strings`, `sync`, `syscall`, `testing`, `time`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/internal/nametransform`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
