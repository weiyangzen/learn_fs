# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/settings.rs

## Purpose
Defines scrypt cost settings and named presets for production, low-memory, paranoid, and test derivations.

## Important APIs, types, and functions
- `ScryptSettings { log_n, r, p, salt_len }`.
- Presets `PARANOID`, `DEFAULT`, `LOW_MEMORY`, and `TEST`.
- Unit test `params_are_valid` validates presets against RustCrypto `scrypt::Params`.

## Control flow
No runtime control flow beyond callers choosing a preset and passing it to `ScryptParams::generate`.

## State and persistence behavior
Settings themselves are not persisted; generated `ScryptParams` persist the chosen numeric values and random salt.

## Dependencies and integration points
Used by KDF generation, examples, tests, and benchmarks. Comments document approximate memory usage for operational tuning.

## Risks and edge cases
Production presets can require large memory allocations, especially `PARANOID` and `DEFAULT`. `TEST` is public despite a TODO to restrict it, so callers could accidentally use weak settings outside tests.

## Test signals
`rstest` validates every preset can generate parameters accepted by `scrypt::Params::new`.
