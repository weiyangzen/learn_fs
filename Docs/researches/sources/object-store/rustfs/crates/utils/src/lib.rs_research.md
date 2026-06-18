# sources/object-store/rustfs/crates/utils/src/lib.rs

## Purpose
Defines the root module graph and public re-export policy for `rustfs-utils`.

## Important APIs, Types, And Functions
Feature gates expose `ip`, `net`, `http`, `retry`, `io`, `hash`, `os`, `path`, `string`, `crypto`, `compress`, `dirs`, and `obj`. Several modules are glob re-exported at crate root: `net`, `hash`, `io`, `ip`, `crypto`, `compress`, `dunce`, `envs`, and `logging`. `logging` and `envs` are always compiled; `obj` is feature-gated but not glob re-exported.

## Control Flow And State
No runtime behavior. Compile-time feature selection controls dependency surface and visible APIs. `retry` is gated by both `net` and `io`, reflecting its dependency on network/http retry classification and stream behavior.

## Dependencies And Integration Points
Integrates all utility submodules into a single crate-level public API. Downstream crates can either use feature-qualified modules or root-level glob exports depending on enabled features.

## Risks And Test Signals
Glob re-exports can create API ambiguity and semver friction when modules add names. Feature combinations need compile coverage because some modules depend on others conditionally. There are no tests in this file; compile checks across feature matrices are the primary signal.
