# sources/object-store/rustfs/crates/common/src/lib.rs

## Purpose
`lib.rs` is the public entry point for `rustfs-common`. It declares common modules, re-exports global/readiness APIs, defines a default delimiter constant, and provides a `defer!` macro for scope-exit cleanup.

## Important APIs, Types, and Functions
Public modules are `bucket_stats`, `globals`, `heal_channel`, `last_minute`, and `metrics`; `readiness` is private but re-exported as `GlobalReadiness` and `SystemStage`. `DEFAULT_DELIMITER` is byte value `44` (`,`). `defer!` creates a local guard whose `Drop` runs a captured block at end of scope.

## Control Flow
Module declarations make submodules available to downstream crates. The `defer!` macro expands to a local `Guard<F: FnOnce()>` with an `Option<F>`; on drop it takes and invokes the closure, discarding the block's return value.

## State and Persistence Behavior
No state is stored in this file beyond constants. State comes from submodules and macro-created stack guards.

## Dependencies and Integration Points
Re-exporting `globals::*` makes process-global setters/getters available through `rustfs_common`. Re-exporting readiness types exposes system readiness coordination. `defer!` can be used throughout the workspace for cleanup patterns without adding a crate dependency.

## Risks and Edge Cases
The macro names its binding `_guard`; multiple `defer!` calls in the same scope may conflict or shadow in ways that affect drop order. Because the macro uses a local type named `Guard`, expansion hygiene should keep it scoped but diagnostics may be less clear. `DEFAULT_DELIMITER` uses a numeric literal rather than `b','`, which is less self-documenting.

## Test Signals
No tests are in this file. Submodule tests validate exported behavior for heal channels and last-minute metrics.
