<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/Cargo.toml -->
# sources/object-store/rustfs/crates/policy/Cargo.toml

Purpose: Defines the `rustfs-policy` crate metadata, dependency graph, lint inheritance, and library settings for RustFS policy management and enforcement code.

Important APIs/types/functions: The package is named `rustfs-policy` and inherits edition, license, repository, rust-version, version, and homepage from the workspace. It documents the crate as policy management for RustFS and disables doctests under `[lib]`.

Control flow: Cargo uses this manifest to compile policy code with workspace lints and dependencies. Runtime behavior is not implemented here, but selected dependency features shape the available APIs: `rustfs-config` enables `constants` and `opa`; `time` enables serde/parsing/formatting/macros; `tokio` uses `full`; `serde` enables derive and rc; `strum` enables derive; `ipnetwork` enables serde.

State/persistence behavior: No runtime state. Build state is governed by workspace lockfiles and feature resolution.

Dependencies/integration: Internal workspace crates include `rustfs-credentials`, `rustfs-config`, and `rustfs-crypto`. External dependencies support async execution (`tokio`, `async-trait`, `futures`, `pollster`), serialization (`serde`, `serde_json`), errors (`thiserror`), enums (`strum`), policy condition evaluation (`ipnetwork`, `base64-simd`, `regex`, `time`, `chrono`), JWT (`jsonwebtoken`), HTTP/OPA (`reqwest`), tracing, and caching (`moka`). Dev dependencies include `test-case` and `temp-env`.

Risks/test signals: The broad `tokio/full` and network-related dependencies increase compile surface for a policy crate. `doctest = false` means examples in docs will not be checked. Manifest correctness is indirectly tested by crate compilation; there are no manifest-specific tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/policy/Cargo.toml -->
