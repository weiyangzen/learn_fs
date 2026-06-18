# sources/security-integrity/gocryptfs/tests/deterministic_names/deterministic_names_test.go

Purpose: Integration or regression test file in the deterministic names tests suite.

Important APIs and types: package `deterministic_names`; functions/tests `TestMain`, `TestDeterministicNames`; key imports `fmt`, `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `path/filepath`, `testing`, `github.com/rfjakob/gocryptfs/v2/internal/configfile`, `github.com/rfjakob/gocryptfs/v2/tests/test_helpers`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
