# sources/object-store/rustfs/crates/security-governance/Cargo.toml

## Purpose
Defines the `rustfs-security-governance` crate, a small contract crate for security governance metadata and validation. It is versioned, licensed, documented, linted, and rust-versioned through workspace settings.

## Dependencies and Integration
The only runtime dependency is workspace `thiserror`, matching the crate's role as pure value types plus validator error enums. Doctests are disabled. The crate exports governance contracts used by other RustFS crates without pulling in async runtimes, serde, storage, or network dependencies.

## Risks and Test Signals
The manifest keeps dependency surface intentionally narrow, which reduces build and security risk. Any future dependency added here should be justified because this crate is likely meant as a lightweight shared policy layer. Tests live in the module source files, not in manifest-level integration tests.
