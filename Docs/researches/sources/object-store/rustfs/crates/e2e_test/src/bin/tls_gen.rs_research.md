# sources/object-store/rustfs/crates/e2e_test/src/bin/tls_gen.rs

## Purpose
This binary is the command-line entry point for generating a RustFS TLS bundle for local TLS and mTLS tests.

## Important APIs, Types, and Functions
It imports `clap::Parser` and `e2e_test::tls_gen::{Args, run}`. `main` parses CLI arguments into `Args`, calls `run`, prints the generated output directory, and returns `anyhow::Result<()>`.

## Control Flow
The flow is a thin wrapper: parse arguments, generate the bundle through the library module, print success output, and propagate any error via `?`.

## State and Persistence
The binary writes no files directly. Persistence is delegated to `tls_gen::run`, which returns the output directory path. The only local side effect is stdout.

## Dependencies and Integration Points
This file depends on the `e2e_test` library exporting `pub mod tls_gen` from `src/lib.rs`, plus the manifest's `clap` and `anyhow` dependencies. It provides a reusable CLI around the same library code that tests can call directly.

## Risks and Edge Cases
There is little logic here, so risk is mostly argument-surface mismatch with `tls_gen::Args`. Errors are not customized at the CLI wrapper layer.

## Test Signals
No direct tests are in this file. The underlying `tls_gen` module has tests for writing a full bundle and rejecting non-positive validity days, which indirectly cover the CLI's called function.
