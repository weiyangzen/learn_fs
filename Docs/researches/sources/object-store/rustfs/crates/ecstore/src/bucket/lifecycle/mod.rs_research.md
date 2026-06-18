# sources/object-store/rustfs/crates/ecstore/src/bucket/lifecycle/mod.rs

## Purpose

This file is the module declaration and public wiring point for the bucket lifecycle package. It exposes the lifecycle submodules and aliases `core` as `lifecycle`, which lets the rest of ecstore import `crate::bucket::lifecycle::lifecycle::{...}` while the implementation file remains named `core.rs`.

## Important APIs, Types, and Functions

The module declarations are:

- `bucket_lifecycle_audit`
- `bucket_lifecycle_ops`
- `core`
- `evaluator`
- `rule`
- `tier_last_day_stats`
- `tier_sweeper`

The only re-export is `pub use self::core as lifecycle;`.

## Control Flow

There is no runtime control flow. Rust module loading makes each child module available, and the `core` re-export establishes the stable import path used by lifecycle operation code and other consumers.

## State and Persistence Behavior

There is no state or persistence in this file.

## Dependencies and Integration Points

This file integrates the lifecycle package with the crate module tree. The alias is important because `bucket_lifecycle_ops.rs` imports `crate::bucket::lifecycle::lifecycle::{ExpirationOptions, Lifecycle, ObjectOpts, TransitionOptions, ...}` and `evaluator.rs` imports `crate::bucket::lifecycle::lifecycle::{Event, Lifecycle, ObjectOpts}`.

Changing this file can break all downstream module paths even though it has no business logic.

## Risks and Edge Cases

- Removing or renaming `pub use self::core as lifecycle` would break existing imports throughout lifecycle operations.
- Adding modules here affects compile visibility but not behavior by itself.
- There are no guards or tests specific to this module declaration file.

## Test Signals

There are no local tests. Compile success of the lifecycle package is the primary signal that module declarations and the `lifecycle` alias remain valid.
