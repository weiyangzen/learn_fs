# sources/object-store/garage/src/garage/tests/k2v_client/mod.rs

Purpose: This module declares integration tests for the typed `k2v-client` crate.

Important APIs and types: It contains only `pub mod simple;`, exposing the client smoke and special-character tests.

Control flow: Rust test discovery compiles and runs the child module when the parent `tests/lib.rs` includes `k2v_client` under the `k2v` feature.

State and persistence behavior: No state is stored here. The child module creates buckets and writes K2V data through `K2vClient`.

Dependencies and integration points: It connects the Garage integration test crate with the `k2v-client` crate's public API tests.

Risks: Additional K2V client tests must be declared here or they will not run. Feature gating can exclude this module from default builds.

Test signals: Compilation of this module ensures the typed client tests are part of the feature-enabled integration suite.
