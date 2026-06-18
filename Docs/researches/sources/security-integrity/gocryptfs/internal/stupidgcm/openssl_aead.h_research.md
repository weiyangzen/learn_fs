# sources/security-integrity/gocryptfs/internal/stupidgcm/openssl_aead.h

Purpose: C/OpenSSL EVP bridge for authenticated encryption and decryption used behind the Go `cipher.AEAD` wrappers.

Important APIs and types: C functions/declarations `openssl_aead_seal`, `openssl_aead_open`, `noop_c_function`. Uses OpenSSL EVP raw buffer ABI.

Control flow: Go cgo wrappers call these C routines with explicit pointers and lengths. The EVP path allocates a context, initializes cipher/key/IV/AAD, processes plaintext or ciphertext, handles the 16-byte tag, and returns length or authentication failure. The subsystem deliberately exposes a narrow AEAD contract: fixed key/nonce/tag sizes, panic-on-programmer-error validation, and `ErrAuth` for corrupted ciphertext. The OpenSSL path crosses cgo into EVP contexts, making buffer length checks, NULL handling for empty slices, and context cleanup important.

State and persistence behavior: No repository persistence. Runtime state is OpenSSL `EVP_CIPHER_CTX` scratch state plus caller-owned buffers; freeing contexts and validating lengths are the key invariants.

Dependencies and integration points: nearby gocryptfs packages, platform syscalls, OpenSSL/go-fuse, or test helpers as implied by the file path.

Risks: main risk is drift between this file and the subsystem contracts it supports.

Test signals: Signals are supplied by nearby unit/integration tests in this subset and by the top-level `test.bash` harness.
