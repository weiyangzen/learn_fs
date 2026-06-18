# sources/security-integrity/cryfs/crates/crypto/src/kdf/scrypt/mod.rs

## Purpose
Top-level scrypt module documenting cost parameters, exporting settings/parameter types, and selecting the default scrypt backend.

## Important APIs, types, and functions
- Re-exports `ScryptParams` and `ScryptSettings`.
- Public `backends` module.
- `pub type Scrypt = backends::scrypt::ScryptScrypt`.

## Control flow
No runtime control flow; it establishes type aliases and module visibility.

## State and persistence behavior
Defines the public path for serialized scrypt parameters used by encrypted data configuration.

## Dependencies and integration points
Used by KDF callers and tests as the default password KDF. Connects settings, serialized parameters, and backend implementations.

## Risks and edge cases
Default backend changes must preserve derived-key compatibility for existing serialized parameters. Documentation advertises high-memory presets that can be expensive in tests/benchmarks.

## Test signals
Includes `tests.rs`, which instantiates generic KDF tests for default and concrete backends.
