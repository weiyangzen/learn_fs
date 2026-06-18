# sources/security-integrity/gocryptfs/tests/example_filesystems/example_filesystems_test.go

Purpose: Integration or regression test file in the example filesystem compatibility suite.

Important APIs and types: package `example_filesystems`; functions/tests `TestMain`, `TestExampleFSv04`, `TestExampleFSv05`, `TestExampleFSv06`, `TestExampleFSv06PlaintextNames`, `TestExampleFSv07`, `TestExampleFSv07PlaintextNames`, `TestExampleFSv09`, `TestExampleFSv11`, `TestExampleFSv11reverse`, `TestExampleFSv11reversePlaintextnames`, `TestExampleFSv13`, `TestExampleFSv13MasterkeyStdin`, `TestExampleFSv13reverse`, `TestExampleFSv22deterministicNames`, `TestExampleFSv22xchacha`, `TestExampleFSv22xchachaDeterministicNames`; key imports `flag`, `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/stupidgcm`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. Reverse mode tests and fixtures protect deterministic encrypted-view behavior and the AES-SIV requirement for safe reverse mounts. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `flag`, `fmt`, `os`, `os/exec`, `syscall`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/stupidgcm`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors; platform syscall semantics and kernel/FUSE differences can change behavior.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
