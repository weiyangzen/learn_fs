# sources/object-store/garage/src/garage/tests/common/ext/mod.rs

Purpose: This tiny module re-exports extension traits used by integration tests.

Important APIs and types: It declares `mod process;` and `pub use process::*;`, exposing `CommandExt` to sibling test modules.

Control flow: There is no runtime control flow beyond Rust module loading. Importing `common::ext::*` makes process command helper methods available.

State and persistence behavior: No state or persistence is present.

Dependencies and integration points: It integrates the test common module with `ext/process.rs`, allowing CLI command invocations in tests to use `.quiet()`, `.expect_success_status()`, and `.expect_success_output()`.

Risks: Because it re-exports everything from `process`, changes to `process.rs` become part of the public helper surface for all tests.

Test signals: Every integration test that invokes the Garage binary with `common::ext::*` depends on this re-export compiling and resolving correctly.
