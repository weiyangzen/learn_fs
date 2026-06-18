# sources/security-integrity/cryfs/crates/rustfs/Cargo.toml

Purpose: Cargo manifest for the `cryfs-rustfs` crate.

Important APIs/types/functions: declares crate metadata, dependencies for async FUSE integration, local CryFS utility/concurrent-store crates, `fuser` 0.17, a renamed `fuser_fusemt` 0.16 for `fuse_mt`, `fuse_mt`, `tokio`, `tokio-util`, `nix`, and examples `inmemory` and `passthrough`.

Control flow: feature flags select backend support: default enables `fuser`, optional `fuse_mt`, and `testutils` forwards test features to dependencies. macOS adds fuser ABI compatibility features.

State and persistence behavior: no runtime state. Dependency versions and features control compiled backend behavior and platform capabilities.

Dependencies and integration points: coordinates high-level, low-level, object-based APIs, tests, and example binaries. Comments explain the dual-fuser dependency caused by `fuse_mt` still using fuser 0.16.

Risks: TODOs note `fuser` should become optional for the feature, and `env_logger`/`nix` are mostly example dependencies. Version skew between fuser 0.17 and fuser 0.16 bridge must be handled carefully.

Test signals: `cargo test -p cryfs-rustfs --features testutils` and building both examples/backends are the main signals.
