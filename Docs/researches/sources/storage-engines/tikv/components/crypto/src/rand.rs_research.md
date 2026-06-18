# sources/storage-engines/tikv/components/crypto/src/rand.rs

Purpose: This module exposes cryptographically strong random bytes and `u64` generation through OpenSSL, keeping encryption-related randomness inside the FIPS-aware crypto shim.

Important APIs and functions: `rand_bytes(buf: &mut [u8]) -> Result<(), ErrorStack>` delegates to `openssl::rand::rand_bytes`. `rand_u64() -> Result<u64, ErrorStack>` fills an 8-byte buffer and returns `u64::from_ne_bytes`.

Control flow: `rand_u64` is a simple wrapper: allocate array, fill using `rand_bytes`, convert to native-endian integer, propagate OpenSSL errors.

State and persistence behavior: No persistent state. Randomness comes from OpenSSL's RNG state.

Dependencies and integration points: `encryption/src/encrypted_file/mod.rs` uses `rand_u64` to create temporary file extensions. Other cryptographic code should prefer this module over the general `rand` crate.

Risks: `from_ne_bytes` is fine for random IDs but produces architecture-endian textual values if later serialized directly. Callers must handle OpenSSL `ErrorStack`.

Test signals: No direct tests in this file; consumers validate random IV/temp-name behavior indirectly.
