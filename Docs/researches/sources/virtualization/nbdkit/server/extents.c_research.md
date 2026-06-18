# File Research: sources/virtualization/nbdkit/server/extents.c

Purpose: Implements public extent-list management and filter helpers for NBD block status/extents.

Data model:
- `struct nbdkit_extents` wraps a vector of `struct nbdkit_extent`.
- Tracks requested `[start, end)` range and `next`, the expected offset for the next appended extent.
- Caps stored extents at `MAX_EXTENTS` = 1 Mi entries.

Public API:
- `nbdkit_extents_new(start, end)` validates `start <= end` and both values within `INT64_MAX`.
- `nbdkit_extents_free`, `nbdkit_extents_count`, and `nbdkit_get_extent` expose lifecycle and access.
- `nbdkit_add_extent` enforces strictly contiguous ascending additions, ignores zero-length entries, truncates to requested range, rejects gaps after `start`, and coalesces adjacent extents with identical type.

Filter helpers:
- `nbdkit_extents_aligned` asks the next backend for a larger aligned range, coalesces or truncates unaligned leading extents, and trims the final result back to the caller’s original offset.
- It intersects type bits when merging, using bitwise AND as the safe representation for mixed regions.
- `nbdkit_extents_full` repeatedly calls `next->extents` with `REQ_ONE` cleared until it covers the whole requested region.

Safety and assumptions:
- Plugin misbehavior is caught with API errors or asserts for no forward progress.
- `nbdkit_extents_full` rejects excessive extent counts with `ENOMEM`.
- These helpers depend on backend `get_size` and `extents` next-ops from the filter chain.
