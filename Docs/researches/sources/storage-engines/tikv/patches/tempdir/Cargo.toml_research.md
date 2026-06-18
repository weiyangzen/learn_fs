# sources/storage-engines/tikv/patches/tempdir/Cargo.toml

## Purpose
Defines a local unpublished compatibility crate named `tempdir` at version `0.3.7`. It lets TiKV satisfy dependencies expecting the old `tempdir` crate while implementing behavior through the maintained `tempfile` crate.

## Important Fields and Control Flow
The manifest sets edition 2021, `publish = false`, and `license = "MIT OR Apache-2.0"`. Its only dependency is `tempfile = "3"`. Cargo has no build script, features, binaries, or examples to process here; it just builds the library in `src/lib.rs` when selected by workspace or patch configuration.

## State, Dependencies, Integration
No persistent state is declared in the manifest. Runtime temporary directory state belongs to the library implementation. The key integration point is dependency override/local patch resolution inside the TiKV source tree.

## Risks and Test Signals
The version intentionally resembles the historical crate, so API compatibility depends on `src/lib.rs`. Test signals are successful downstream `cargo check`, dependency graph resolution selecting this local crate, and tests that exercise tempdir creation, cleanup, and persistence.
