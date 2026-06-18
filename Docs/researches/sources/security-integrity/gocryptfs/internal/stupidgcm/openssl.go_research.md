# sources/security-integrity/gocryptfs/internal/stupidgcm/openssl.go

Purpose: OpenSSL-backed AEAD implementation code for AES-GCM, ChaCha20-Poly1305, or XChaCha20-Poly1305.

Important APIs and types: build tags: cgo && !without_openssl; package `stupidgcm`; functions/tests `openSSLSeal`, `openSSLOpen`, `slicePointerOrNull`, `noopCFunction`; key imports `fmt`, `log`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important. Key material is copied into package-owned storage and wipe methods try to zero it, but Go memory copies remain a best-effort limitation.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `fmt`, `log`

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
