# sources/object-store/rustfs/crates/utils/src/http/mod.rs

## Purpose
Defines the public HTTP utility module surface for the `rustfs-utils` crate.

## Important APIs, Types, And Functions
Declares `header_compat`, `headers`, `ip`, and `metadata_compat`, then glob re-exports all four modules. This lets callers import HTTP constants, metadata compatibility helpers, proxy source-IP helpers, and dual-prefix header helpers from `rustfs_utils::http::*`.

## Control Flow And State
There is no runtime control flow or state. Its behavior is compile-time module composition.

## Dependencies And Integration Points
Depends on sibling HTTP modules. It is gated by `#[cfg(feature = "http")]` in `lib.rs`, so the whole API surface appears only when the crate's `http` feature is enabled.

## Risks And Test Signals
Glob re-exports make naming conflicts possible as the HTTP utility surface grows. There are no direct tests; validation is through successful compilation and tests in child modules.
