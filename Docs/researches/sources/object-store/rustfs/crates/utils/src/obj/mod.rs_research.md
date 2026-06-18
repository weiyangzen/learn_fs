# sources/object-store/rustfs/crates/utils/src/obj/mod.rs

## Purpose
Defines the public object utility module surface.

## Important APIs, Types, And Functions
Declares the private `metadata` module and re-exports its public items, currently `extract_user_defined_metadata`.

## Control Flow And State
No runtime logic or state. This is a compile-time module wrapper.

## Dependencies And Integration Points
Enabled by `#[cfg(feature = "obj")]` in `lib.rs`. It gives downstream callers a stable `rustfs_utils::obj::*` location for object-related helpers.

## Risks And Test Signals
Glob re-export is small today but can become ambiguous as object utilities grow. There are no direct tests; the child metadata module carries the behavioral tests.
