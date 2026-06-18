# sources/security-integrity/fscrypt/crypto/rand.go

## Purpose
`rand.go` centralizes secure random generation for fscrypt keys and generated passphrases using Linux `getrandom(2)` in nonblocking mode. It intentionally avoids returning bytes before the kernel entropy pool is initialized.

## Important APIs, Types, and Functions
`NewRandomBuffer(length)` returns a random byte slice. `NewRandomKey(length)` returns a locked `*Key` filled from the same source. `NewRandomPassphrase(length)` produces lowercase alphabetic random passphrases. `randReader` implements `io.Reader` over `unix.Getrandom`.

## Control Flow
`NewRandomBuffer` calls `io.ReadFull(randReader{}, buffer)`. `NewRandomKey` delegates to `NewFixedLengthKeyFromReader`. `NewRandomPassphrase` allocates a protected key, repeatedly obtains twice as many raw bytes as remaining characters, rejects values in the modulo-bias tail, maps accepted values to `a` through `z`, and wipes each temporary raw key.

## State and Persistence
No state persists beyond returned buffers or keys. Temporary raw random keys used during passphrase creation are wiped. The functions depend on kernel RNG state and return errors instead of blocking when entropy is unavailable.

## Dependencies and Integration Points
Depends on `golang.org/x/sys/unix` for `Getrandom`, `io.ReadFull`, and the package's `Key` allocation path. It supplies random policy/internal keys and recovery test fixtures to crypto, filesystem metadata, and keyring tests.

## Risks
`GRND_NONBLOCK` means startup on low-entropy systems can fail and callers must handle that. `NewRandomBuffer` returns ordinary heap bytes rather than locked memory, so it is less appropriate for long-lived secrets. `NewRandomPassphrase` only uses lowercase letters; it is random but intentionally constrained.

## Test Signals
Crypto tests outside this specific file check that generated keys exist, large key generation works, and random buffers are not trivially compressible or equal. Recovery tests rely on `NewRandomKey` for round-trip test inputs.
