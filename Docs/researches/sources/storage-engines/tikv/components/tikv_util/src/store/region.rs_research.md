# sources/storage-engines/tikv/components/tikv_util/src/store/region.rs

## Purpose
Provides key-range membership and store-membership helpers for `kvproto::metapb::Region`.

## Important APIs, Types, and Functions
- `check_key_in_region_exclusive` checks `(start_key, end_key)`.
- `check_key_in_region_inclusive` checks `[start_key, end_key]`.
- `check_key_in_region` checks `[start_key, end_key)`.
- `region_on_same_stores` compares peer store IDs, roles, and witness flags between two regions.
- `region_on_stores` checks if a region has any peer on target stores, with empty target list meaning true.

## Control Flow
Range checks compare byte slices and treat an empty end key as unbounded. Store comparison first requires equal peer counts, then ensures every left peer has a right peer with matching store ID, role, and witness status. `region_on_stores` performs nested `any` checks.

## State and Persistence Behavior
All helpers are pure reads over supplied region values.

## Dependencies and Integration Points
Depends on `kvproto::metapb::Region`, re-exported by `store/mod.rs`, and used by region movement, placement, and validation logic.

## Risks
`region_on_same_stores` assumes at most one replica per store for the same region; duplicate peers could make equality semantics ambiguous. Boundary inclusivity differs across the three range helpers, so callers must choose carefully.

## Test Signals
Tests cover empty/unbounded ranges, boundary inclusion/exclusion, same-store comparisons with voter/learner/witness distinctions through store module tests, and target-store membership.
