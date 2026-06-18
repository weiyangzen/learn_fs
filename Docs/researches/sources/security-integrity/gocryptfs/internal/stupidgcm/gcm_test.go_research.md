# sources/security-integrity/gocryptfs/internal/stupidgcm/gcm_test.go

Purpose: Regression tests for the OpenSSL-backed AEAD implementations, comparing them with Go reference ciphers and checking tamper, buffer, concurrency, malformed-input, and key-wipe behavior.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `TestStupidGCM`; key imports `crypto/aes`, `crypto/cipher`, `testing`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `crypto/aes`, `crypto/cipher`, `testing`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: This file is itself a test signal; success means the described regression or compatibility behavior still holds. Assertions and subprocess exit codes in the file provide direct pass/fail evidence.
