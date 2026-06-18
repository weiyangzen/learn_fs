<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/lib.rs -->
# sources/object-store/rustfs/crates/config/src/lib.rs

## Purpose
Feature-gated crate root for RustFS configuration constants and optional audit, notify, observability, OPA, and server-config modules.

## Important APIs, types, and functions
With `constants`, it exposes `pub mod constants` and re-exports each constants submodule at crate root, plus a nested `oidc` module. Optional modules are gated by `audit`, `notify`, `observability`, `opa`, and `server-config-model` features.

## Control flow
No runtime flow. Compile-time feature selection determines the public API surface.

## State and persistence behavior
No state or persistence. It controls which constants and config modules are linkable by dependent crates.

## Dependencies and integration points
Integrates with Cargo features and downstream crates that import constants from `rustfs_config::*`.

## Risks and edge cases
Public re-export changes are semver-sensitive. The nested `oidc` re-export differs from most constants modules and must stay documented for callers. Missing feature flags can make modules disappear at compile time.

## Test signals
Feature-matrix compilation is the main test signal. API tests should import representative constants and optional modules under their feature flags.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/lib.rs -->
