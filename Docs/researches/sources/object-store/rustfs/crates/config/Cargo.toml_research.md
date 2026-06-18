# sources/object-store/rustfs/crates/config/Cargo.toml

## Purpose
Defines the `rustfs-config` crate, which centralizes application constants and feature-gated configuration key sets for audit, notify, observability, OPA, and server config models.

## Important APIs, types, and functions
Default feature is `constants`. Optional features enable `const-str`, `serde`, and `serde_json` dependencies as needed. Package metadata identifies the crate as configuration management for RustFS.

## Control flow
Feature resolution controls which modules can compile. The `audit`, `notify`, and `constants` features enable compile-time string concatenation; `server-config-model` enables serialization dependencies.

## State and persistence behavior
No runtime state is defined. The manifest controls compile-time availability and dependency inclusion.

## Dependencies and integration points
This crate feeds constants to server startup, admin config, audit target parsing, observability setup, and model serialization code. Workspace lint settings apply.

## Risks and edge cases
Consumers that expect audit constants need the `audit` feature, while default builds only include constants. Doctests are disabled for the library, so example drift would not be caught by doctest.

## Test signals
Validation is through cargo feature builds and the unit tests in constant modules.
