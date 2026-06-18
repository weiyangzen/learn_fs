# sources/object-store/rustfs/crates/notify/src/event_bridge.rs

## Purpose
Compatibility/re-export module for the live event bridge API. It exposes `LiveEventHistory` and `NotifyEventBridge` from `pipeline`.

## Important APIs, types, and functions
- `pub use crate::pipeline::{LiveEventHistory, NotifyEventBridge};`
- `NotifyEventBridge` is a type alias to `NotifyPipeline` in `pipeline.rs`.

## Control flow
No local control flow exists. Callers importing from `event_bridge` receive the pipeline implementation.

## State and persistence behavior
State is owned by `NotifyPipeline` and `LiveEventHistory`; this file stores nothing.

## Dependencies and integration points
Integrates older or semantically clearer bridge naming with the current pipeline module. It is re-exported from `lib.rs`.

## Risks and edge cases
Because this is only a re-export, documentation or API drift must be tracked in `pipeline.rs`. Removing it would be a public API break for consumers using `NotifyEventBridge`.

## Test signals
No direct tests. Coverage comes from pipeline/live event tests.
