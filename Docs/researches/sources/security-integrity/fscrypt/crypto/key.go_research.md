# sources/security-integrity/fscrypt/crypto/key.go

## Purpose
`key.go` defines the `crypto.Key` abstraction used throughout fscrypt to hold sensitive key and passphrase material. It allocates key buffers with `mmap`, optionally asks the kernel to keep pages locked, wipes buffers before freeing them, and provides helpers for reading keys from Go or C inputs. It also encodes and decodes human-transcribable recovery codes for policy keys.

## Important APIs, Types, and Functions
`UseMlock` controls whether allocations use `MAP_LOCKED`. `Key` wraps a private `[]byte` buffer. `NewBlankKey`, `NewKeyFromReader`, `NewFixedLengthKeyFromReader`, and `NewKeyFromCString` are construction paths. `Wipe`, `Len`, `Equals`, `Data`, `UnsafePtr`, `UnsafeToCString`, and `Clone` expose lifecycle or interop operations. `WriteRecoveryCode` and `ReadRecoveryCode` convert `metadata.PolicyKeyLen` keys to and from base32 blocks separated by dashes.

## Control Flow
`NewBlankKey` validates size, maps anonymous private memory, translates `EAGAIN` into the package-level mlock-limit error, and installs a finalizer that calls `Wipe`. `NewKeyFromReader` starts with one page, reads until EOF, doubles capacity when full, then shrinks to the actual read length. Recovery-code writing validates key length, encodes into a temporary locked key, and writes fixed-size base32 blocks. Reading performs the inverse sequence, validating separators before base32 decoding.

## State and Persistence
State is in process memory only. Sensitive buffers are zeroed before `munmap`; recovery encoding uses temporary `Key` buffers that are wiped on return. The only external persistence is whatever caller-supplied `io.Writer` receives for recovery codes.

## Dependencies and Integration Points
This file depends on `golang.org/x/sys/unix` for memory mapping, `crypto/subtle` for constant-time equality, cgo for C string interop, `metadata` constants for key lengths, and `util` helpers for pointer conversion, min, length checks, and error-aware readers/writers. Key objects feed key wrapping, metadata protectors, kernel keyring payloads, and PAM secret handling.

## Risks
`Key` is explicitly not thread-safe; concurrent use and wipe can race or double-free. `Data`, `UnsafePtr`, and `UnsafeToCString` bypass some safety guarantees, especially because the C copy is not locked or automatically wiped. A caller that relies only on the finalizer keeps secrets resident longer than needed. Recovery codes are equivalent to raw policy keys and must be treated as high-value secrets.

## Test Signals
`recovery_test.go` exercises recovery-code determinism, encode/decode round trips, invalid lengths, bad characters, bad separators, and benchmarks. Broader `crypto` tests outside this subset cover key allocation, wiping, resizing, random generation, wrapping, descriptor derivation, and passphrase hashing.
