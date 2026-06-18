# sources/object-store/openstack-swift/swift/common/ring/composite_builder.py

## Purpose
`composite_builder.py` builds and manages composite Swift rings made from multiple independently-built component rings. Composite rings provide stronger placement guarantees across failure domains, such as ensuring replicas/fragments are split across regions, by concatenating component assignment tables while preserving component order.

## Important APIs, types, and functions
Validation helpers include `pre_validate_all_builders()`, `check_for_dev_uniqueness()`, `check_builder_ids()`, `check_same_builder()`, `is_builder_newer()`, and `check_against_existing()`. Composition helpers include `_make_composite_ring()`, `compose_rings()`, `_make_component_meta()`, and `_make_composite_metadata()`. `CompositeRingBuilder` loads component builders, composes ring data, persists composite metadata, validates component consistency, cooperatively rebalances components, and coordinates partition movement. `CooperativeRingBuilder` subclasses `RingBuilder` so component builders delegate movement checks to the parent composite builder.

## Control flow and state behavior
Composition begins by validating that at least two builders exist, all have matching `part_power`, replica counts are integers, no builder has unapplied device changes, regions are not shared across builders, and no `ip/port/device` tuple appears in multiple builders. `_make_composite_ring()` deep-copies component devices and assignment arrays, resizes device-id arrays if needed, offsets device ids by cumulative device count, concatenates assignment tables, and returns `RingData`.

`CompositeRingBuilder` persists metadata as JSON with component id/version/replica information and builder-file paths. Loading reconstructs the builder-file list from metadata. `_load_components()` loads `CooperativeRingBuilder` instances, validates builder ids, and checks that existing composite metadata still matches unless forced. `compose()` updates ring data, version, and component metadata. `rebalance()` loads components, synchronizes last-part-move epochs, shuffles rebalance order, rebalances and validates each component, saves all builders, and returns results in component order.

## Dependencies and integration points
The module depends on `RingBuilder`, `RingData`, `RingBuilderError`, ring utility functions `calc_dev_id_bytes` and `resize_array`, plus standard `copy`, `json`, `os`, `shuffle`, `defaultdict`, and `combinations`. It is used by Swift ring-building tools for multi-region or duplicated erasure-code placement policies. The resulting `RingData` is saved and loaded by the normal ring runtime.

## Risks and edge cases
Component order is critical because primary-node indexes change if order changes, which can move erasure-coded fragments. Existing-composite checks enforce builder id and replica equality but require builders to have persisted ids. Region uniqueness is stricter than normal rings and may surprise operators. Device uniqueness only checks `ip`, `port`, and `device`, not replication addresses. JSON metadata writes are not atomic. Cooperative rebalancing saves component builders only after all rebalance/validation passes, but an exception while saving later files can leave earlier files persisted.

## Test signals
Tests should cover validation errors for too few builders, mismatched part power, fractional replicas, dirty builders, shared regions, duplicate devices, missing/duplicate builder ids, old/new component metadata comparisons, device id offsetting, dev-id-byte resizing, metadata save/load, compose force and require-modified modes, cooperative `can_part_move()` behavior, shuffled rebalance with ordered results, and component save failure handling.
