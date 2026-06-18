# sources/security-integrity/gocryptfs/internal/stupidgcm/prefer.go

Purpose: Backend-preference heuristics deciding when OpenSSL crypto should be preferred over Go crypto on this platform.

Important APIs and types: package `stupidgcm`; functions/tests `PreferOpenSSLAES256GCM`, `PreferOpenSSLXchacha20poly1305`, `HasAESGCMHardwareSupport`; key imports `runtime`

Control flow: Control enters through Go tests, package initialization, or the functions listed above. The file exercises mounted filesystem behavior, subprocess CLI flows, dirfd-relative syscalls, platform shims, logging, or crypto constructors according to its package. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext.

State and persistence behavior: State is primarily temporary test filesystem state, process-global logger/credential/OpenSSL state, or in-memory crypto/syscall buffers. Persistent effects are limited to config files, mountpoints, sockets, xattrs, benchmark/profile artifacts, or fixture data explicitly created by the tests.

Dependencies and integration points: `runtime`

Risks: some checks are timing-sensitive.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
