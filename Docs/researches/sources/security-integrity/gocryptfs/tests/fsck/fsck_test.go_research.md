# sources/security-integrity/gocryptfs/tests/fsck/fsck_test.go

Purpose: Integration or regression test file in the fsck tests suite.

Important APIs and types: package `fsck`; functions/tests `dec64`, `TestBrokenFsV14`, `TestMalleableBase64`, `TestExampleFses`, `TestTerabyteFile`; key imports `encoding/base64`, `os`, `os/exec`, `runtime`, `strings`, `syscall`, `testing`, `time`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `encoding/base64`, `os`, `os/exec`, `runtime`, `strings`, `syscall`, `testing`, `time`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior; some checks are timing-sensitive.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
