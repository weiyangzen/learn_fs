# sources/object-store/rustfs/crates/ecstore/src/bucket/mod.rs

Purpose: Declares the bucket module tree for `ecstore`. It is the public composition point for bucket subsystems such as metadata, policy, lifecycle, replication, quota, versioning, object lock, tagging, targets, and migration.

Important APIs and types: The file exports most child modules with `pub mod`, keeps `msgp_decode` private to the bucket module, and gates `metadata_test` behind `#[cfg(test)]`.

Control flow and state: There is no runtime logic. Its state impact is compile-time module visibility. Private `msgp_decode` limits low-level MessagePack helpers to internal bucket metadata code.

Dependencies and integration: Downstream code imports bucket APIs through these module declarations. `metadata.rs` uses sibling modules such as `quota`, `target`, `object_lock`, and `versioning`; `metadata_sys`, `policy_sys`, and `object_lock` rely on this layout.

Risks: Public module exports define the crate's internal API surface. Adding modules here may expose unstable implementation details. The test module split means codec compatibility tests in `metadata_test.rs` are compiled only for test builds.

Test signals: No direct tests. The file is validated indirectly by the Rust compiler and by tests under declared modules.
