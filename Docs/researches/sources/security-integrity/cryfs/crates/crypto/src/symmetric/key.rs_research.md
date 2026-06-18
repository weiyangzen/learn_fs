# sources/security-integrity/cryfs/crates/crypto/src/symmetric/key.rs

## Purpose
Defines `EncryptionKey`, the protected-memory key container used by symmetric ciphers and KDF outputs.

## Important APIs, types, and functions
- `EncryptionKey { key_data, _lock_guard }`.
- `new`, `from_hex`, `to_hex`, `as_bytes`, `num_bytes`, `take_bytes`, `skip_bytes`, and `generate_random`.
- `Drop` zeroes key bytes with `sodiumoxide::utils::memzero`.

## Control flow
`new` allocates zeroed boxed bytes, attempts to lock memory pages with `region::lock`, warns on failure, calls the initializer closure, then stores optional lock guard. Split helpers copy portions into new protected keys. Random generation fills key bytes from `rand`.

## State and persistence behavior
Key bytes live in heap memory with best-effort mlock and are zeroed on drop. `to_hex`/`from_hex` intentionally expose/copy key material and are marked by TODO as test-only candidates but are currently public.

## Dependencies and integration points
Used by ciphers and KDFs. Logging reports lock failures without failing functionality. `lockable::InfallibleUnwrap` is used by infallible constructors.

## Risks and edge cases
Memory locking is best-effort and may fail silently except for a warning. Public `to_hex` and `from_hex` bypass secret-protection goals. `take_bytes` and `skip_bytes` panic on out-of-bounds slicing.

## Test signals
Key behavior is indirectly tested through KDF and cipher tests that compare hex output, key sizes, deterministic seeded keys, and wrong-key decrypt failures.
