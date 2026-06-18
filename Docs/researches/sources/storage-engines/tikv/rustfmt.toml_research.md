# sources/storage-engines/tikv/rustfmt.toml

## Purpose
Defines repository-wide Rust formatting policy using Rust 2024 style and unstable rustfmt features. It works in tandem with the pinned nightly toolchain.

## Important Settings and Control Flow
The config enables `style_edition = "2024"` and `unstable_features = true`. It wraps and normalizes comments, formats code in doc comments, macro bodies, and macro matchers, normalizes doc attributes, condenses wildcard suffixes, forces Unix newlines, enables field-init and try shorthand, and groups imports by crate with crate-level import granularity. Rustfmt reads this file and rewrites source formatting deterministically.

## State, Dependencies, Integration
No runtime state is stored, but running rustfmt can create broad source diffs. It depends on a rustfmt version that supports the unstable settings and integrates with CI format checks and editor formatting.

## Risks and Test Signals
Nightly rustfmt changes can alter output, especially for unstable options and macro/doc-comment formatting. `cargo fmt --check` under `nightly-2026-01-30` is the primary validation signal; unexpected large diffs indicate toolchain or policy drift.
