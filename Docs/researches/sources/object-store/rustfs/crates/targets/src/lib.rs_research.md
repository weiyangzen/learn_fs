# sources/object-store/rustfs/crates/targets/src/lib.rs

## Purpose
Crate root and public API surface for `rustfs_targets`. It wires submodules together, re-exports target/plugin/runtime/config APIs, and defines the generic `TargetLog` event container.

## Important APIs, types, and functions
- Declares modules for ARN, catalog, config, control plane, domain, errors, manifest, networking, plugin registry, runtime, store, system user-agent helpers, and target implementations.
- Re-exports extension schema builders, connectivity checks, config normalization/builders, control-plane planning APIs, manifests, plugin descriptors/registry, runtime manager/adapters/registries/sidecars, `EventName`, user-agent helpers, `Target`, and `TargetDeliverySnapshot`.
- `TargetLog<E>` serializes as PascalCase and contains `event_name`, `key`, and `records`.

## Control flow
There is no runtime control flow. The file defines what downstream crates can import from `rustfs_targets` without depending on internal module paths.

## State and persistence behavior
No persistent state is owned here. `TargetLog` is a serializable payload model that downstream targets can store or send.

## Dependencies and integration points
The root integrates internal modules and external crates `rustfs_s3_types` and `serde`. It is the compatibility boundary for admin, server, and target code that imports this crate.

## Risks and edge cases
Because it re-exports many internal symbols, changes here are API-significant. Private modules such as `check` and `net` still expose selected symbols through re-exports, so accidental omission can break callers even if the underlying code remains intact.

## Test signals
No direct tests live in this file. Compilation of downstream modules and tests is the primary signal that the re-export surface remains coherent.
