# sources/security-integrity/gocryptfs/internal/stupidgcm/without_openssl.go

Purpose: No-cgo/no-OpenSSL fallback API that prevents accidental OpenSSL backend use in builds compiled without OpenSSL support.

Important APIs and types: build tags: !cgo || without_openssl; package `stupidgcm`; functions/tests `errExit`, `NewAES256GCM`, `NewChacha20poly1305`, `NewXchacha20poly1305`; key imports `fmt`, `os`, `crypto/cipher`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `os`, `crypto/cipher`, `github.com/rfjakob/gocryptfs/v2/internal/exitcodes`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
