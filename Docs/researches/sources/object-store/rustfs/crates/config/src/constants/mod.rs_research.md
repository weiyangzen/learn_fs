<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/mod.rs -->
# sources/object-store/rustfs/crates/config/src/constants/mod.rs

## Purpose
Collects all config constant submodules under one internal module tree.

## Important APIs, types, and functions
Declares `pub(crate) mod` entries for app, body limits, capacity, compress, console, drive, env, heal, health, internode, object, oidc, profiler, protocols, proxy, quota, runtime, scanner, targets, tls, workload, and zero_copy.

## Control flow
No executable flow; Rust module resolution wires submodules for `lib.rs` feature-gated re-exports.

## State and persistence behavior
No runtime state. Its only persistence effect is compile-time module availability.

## Dependencies and integration points
Used by `config/src/lib.rs` when the `constants` feature is enabled.

## Risks and edge cases
Adding a constants file without registering it here prevents downstream re-export. Removing or renaming modules is a public API break for `rustfs-config` constant consumers.

## Test signals
Compilation with the `constants` feature is the primary signal. Public API checks should ensure expected modules remain reachable from the crate root.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/config/src/constants/mod.rs -->
