# sources/security-integrity/gocryptfs/tests/defaults/acl_test.go

Purpose: Integration or regression test file in the defaults tests suite.

Important APIs and types: package `defaults`; functions/tests `TestCpA`, `getfacl`, `TestAcl543`, `TestXattrOverflow`; key imports `math/rand`, `os`, `os/exec`, `path/filepath`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `math/rand`, `os`, `os/exec`, `path/filepath`, `syscall`, `testing`, `golang.org/x/sys/unix`, `github.com/pkg/xattr`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
