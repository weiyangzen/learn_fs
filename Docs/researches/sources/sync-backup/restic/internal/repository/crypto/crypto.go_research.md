## sources/sync-backup/restic/internal/repository/crypto/crypto.go

Purpose: restic encryption and authentication primitive implementing `cipher.AEAD`-like semantics with AES-256 CTR and Poly1305-AES.

Important APIs/types: constants define AES key size, MAC key split, IV size, MAC size, and `Extension`. `ErrUnauthenticated` signals MAC failure. `Key` embeds `MACKey` and `EncryptionKey`. Random constructors `NewRandomKey` and `NewRandomNonce` panic on insufficient entropy. JSON marshal/unmarshal methods serialize key material. `Valid` methods reject all-zero key parts. Low-level helpers include `poly1305MAC`, `macKeyFromSlice`, `poly1305PrepareKey`, `poly1305Verify`, `validNonce`, and `sliceForAppend`. `Key.Seal` validates key, rejects additional data, requires valid nonce, AES-CTR encrypts plaintext, appends Poly1305 tag, and supports exact aliasing/append. `Key.Open` validates key/nonce/length, verifies MAC, then decrypts.

Control flow and state: `Seal` panics for invalid programmer inputs such as invalid key, additional data, bad nonce length, or zero nonce. `Open` returns errors for invalid key, zero nonce, short ciphertext, or authentication failure but panics for bad nonce length. The nonce is external state; callers must ensure uniqueness.

Dependencies and integration points: used by repository key handling, pack encryption/decryption, debug repair tooling, and KDF output. It imports standard crypto plus `golang.org/x/crypto/poly1305` and restic errors.

Risks and test signals: nonce reuse would break confidentiality; zero nonce is rejected but uniqueness is not enforceable here. Additional authenticated data is not supported despite the AEAD interface signature. JSON unmarshal copies whatever bytes are present into fixed arrays, so validation must be called. Tests cover Poly1305 vectors, encrypt/decrypt, tamper detection, nonce validation, aliasing and append behavior, and benchmarks.
