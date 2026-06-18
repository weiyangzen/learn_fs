# sources/object-store/garage/src/garage/tests/k2v/mod.rs

Purpose: This module declares the raw K2V integration test submodules.

Important APIs and types: It exports `batch`, `errorcodes`, `item`, `poll`, and `simple` modules when the parent test crate enables the `k2v` feature.

Control flow: Rust's test harness discovers tests from these child modules through normal module inclusion. There is no additional runtime logic here.

State and persistence behavior: This file has no state. Its child modules create buckets and mutate K2V data through the shared integration context.

Dependencies and integration points: It is included from `tests/lib.rs` under `#[cfg(feature = "k2v")]`, tying K2V tests to feature-enabled builds.

Risks: Adding a K2V test file without declaring it here will leave it uncompiled. Feature gating can hide K2V regressions in builds that do not enable `k2v`.

Test signals: Successful compilation and discovery of the listed K2V modules.
