# sources/security-integrity/gocryptfs/internal/stupidgcm/doc.go

Purpose: Package documentation for the OpenSSL-backed AEAD compatibility layer used by gocryptfs when OpenSSL crypto is selected.

Important APIs and types: package `stupidgcm`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: panic paths are intentional for programmer errors but must not be reachable from untrusted malformed ciphertext except where tests expect ordinary errors.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
