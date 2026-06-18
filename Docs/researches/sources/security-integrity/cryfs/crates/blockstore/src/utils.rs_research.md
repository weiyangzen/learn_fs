# sources/security-integrity/cryfs/crates/blockstore/src/utils.rs

Purpose: This file defines small result enums shared by blockstore operations. `TryCreateResult` reports whether an atomic create inserted a block or found an existing id, and `RemoveResult` reports whether removal deleted a block or found nothing.

Important APIs and flow: Both enums derive equality/debug traits and are marked `#[must_use]`, encouraging callers and tests to inspect operation outcomes instead of treating the operations as fire-and-forget.

State and persistence: The enums represent persistent state transitions at the API boundary: successful creation/removal changes the backing store, while already-exists/not-found variants leave it unchanged.

Dependencies and integration: These types are imported by low-level implementations and tests, and external crates can match on them through the blockstore crate API. They avoid overloading `Result` errors for expected existence races.

Risks and test signals: The enum names are explicit and stable, but adding variants would require updating exhaustive matches. The low-level conformance tests assert exact values for all core create/remove paths.
