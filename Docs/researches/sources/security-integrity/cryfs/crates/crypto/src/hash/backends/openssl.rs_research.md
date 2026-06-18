# sources/security-integrity/cryfs/crates/crypto/src/hash/backends/openssl.rs

## Purpose
Default SHA-512 hash backend using OpenSSL.

## Important APIs, types, and functions
- `OpensslSha512` implements `HashAlgorithmDef` and `HashAlgorithm<64, 8>`.
- Uses `openssl::sha::Sha512`.

## Control flow
Initializes an OpenSSL SHA-512 hasher, updates with salt then data, finishes, wraps bytes in `Digest`, and returns `Hash`.

## State and persistence behavior
Stateless except for local hasher state. Salt is preserved in the returned `Hash` for future verification.

## Dependencies and integration points
Integrated as `pub type Sha512 = backends::OpensslSha512` in the parent module and benchmarked against alternate backends.

## Risks and edge cases
OpenSSL output must remain byte-identical to other backends because compatibility tests assert exact vectors. Native OpenSSL build/runtime behavior can affect portability.

## Test signals
Generic hash tests instantiate both `Sha512` and `OpensslSha512`, checking exact digest vectors and backend parity.
