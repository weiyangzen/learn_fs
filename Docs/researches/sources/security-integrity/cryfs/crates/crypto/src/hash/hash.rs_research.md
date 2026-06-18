# sources/security-integrity/cryfs/crates/crypto/src/hash/hash.rs

## Purpose
Defines the common `Hash` result type that bundles a digest with the salt used to compute it.

## Important APIs, types, and functions
- `Hash<const DIGEST_LEN: usize, const SALT_LEN: usize>` with public `digest` and `salt` fields.
- Associated constants `DIGEST_LEN` and `SALT_LEN`.

## Control flow
No runtime control flow beyond type construction by backends.

## State and persistence behavior
Copyable value type holding digest and salt. The public fields make serialization/storage the caller's responsibility.

## Dependencies and integration points
Connects `Digest` and `Salt` and is the return value for `HashAlgorithm::hash` across all backends.

## Risks and edge cases
Public fields keep the API simple but allow callers to mix digest/salt values manually. Const generic dimensions enforce length consistency at compile time.

## Test signals
Behavior is indirectly tested by hash backend tests that compare digest and salt preservation.
