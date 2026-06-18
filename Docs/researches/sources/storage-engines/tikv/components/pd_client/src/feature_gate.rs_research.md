# sources/storage-engines/tikv/components/pd_client/src/feature_gate.rs

## Purpose
`feature_gate.rs` tracks the maximum observed cluster version and answers whether a version-gated feature can be enabled.

## Important APIs, Types, and Functions
- `FeatureGate` wraps `Arc<AtomicU64>`.
- `set_version` parses a semver string, encodes major/minor/patch into a `u64`, and updates the atomic only if the new value is greater than the current value.
- `can_enable` compares the current encoded version with a `Feature`.
- `reset_version` unsafely overwrites the version and is documented as violating monotonicity unless used carefully.
- `Feature::require` constructs a required version at compile time.

## Control Flow
`set_version` loops with `compare_exchange_weak`; if the new version is not greater than the current version it returns `Ok(false)`. Successful upgrade returns `Ok(true)`.

## State and Persistence Behavior
State is process-local and monotonic under safe APIs. It is updated from PD store heartbeat responses in both client implementations.

## Dependencies and Integration Points
Uses `semver` parsing. `PdClient::feature_gate` lets other components query feature availability based on cluster version.

## Risks
`ver_to_val` assumes major/minor/patch fit under 16-bit minor/patch packing expectations documented in comments, but it does not enforce bounds. Pre-release/build metadata is ignored after parsing. Unsafe reset can lower the version and break monotonic correctness.

## Test Signals
No local tests in this file; behavior is indirectly tested by clients or feature-gated components.
