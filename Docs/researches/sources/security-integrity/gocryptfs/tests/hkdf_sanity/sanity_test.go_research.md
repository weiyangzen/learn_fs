# sources/security-integrity/gocryptfs/tests/hkdf_sanity/sanity_test.go

Purpose: Integration or regression test file in the hkdf sanity tests suite.

Important APIs and types: package `hkdf_sanity`; functions/tests `TestBrokenContent`, `TestBrokenNames`; key imports `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. HKDF flags are compatibility-critical because content and name key derivation changes must not be silently ignored.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `os`, `testing`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
