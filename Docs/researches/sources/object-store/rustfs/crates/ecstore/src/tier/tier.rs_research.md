# sources/object-store/rustfs/crates/ecstore/src/tier/tier.rs

## Purpose

Implements the tier configuration manager: tier map, warm-backend driver cache, add/edit/remove/list/verify operations, config persistence, reload, legacy/external format compatibility, and migration from legacy metadata-bucket locations.

## Important APIs and Types

`TierConfigMgr` stores `tiers`, skipped `driver_cache`, and `last_refreshed_at`. Main methods are `new`, `unmarshal`, `marshal`, `add`, `remove`, `verify`, `list_tiers`, `get`, `edit`, `get_driver`, `reload`, `save`, `save_tiering_config`, `refresh_tier_config`, and `init`. External compatibility DTOs encode `tier-config.bin` with format/version headers and provider type ids.

## Control Flow

Add validates uppercase/non-duplicate tier names, constructs a backend, optionally rejects non-empty backends, then updates tier and driver maps. Remove obtains a driver, optionally checks remote emptiness, and removes maps. Edit clones the redacted config, applies provider-specific credential updates, constructs a new backend, then replaces config/cache. `get_driver` lazily constructs drivers.

Load first reads `config/tier-config.bin`, decodes legacy JSON or external binary, falls back to `tier-config.json`, and initializes an empty config on the first local cluster node if absent. Save encodes external binary and writes to `.rustfs.sys` with max parity. Migration copies compatible legacy config from RustFS or migrating metadata buckets when the target does not already exist.

## State and Persistence Behavior

Persistent state is the tier config object in `RUSTFS_META_BUCKET`. `driver_cache` is in-memory only and rebuilt after reload. Secrets are persisted in config but redacted by `TierConfig` clone/list behavior.

## Dependencies and Integration Points

Integrates with admin errors, `TierCreds`, `TierConfig`, warm-backend factory/probe, object IO APIs, global object-store handle resolution, metadata bucket constants, `read_config`, first-node detection, serde JSON, rmp-serde, Tokio timers, and tracing.

## Risks and Edge Cases

`new_warm_backend(..., true)` receives a probe flag that the visible factory does not use. Add error mapping relies on substring checks. Migration skips incompatible configs with debug logging. `refresh_tier_config` uses one jitter value for the task lifetime. `clear_tier` ignores its `force` argument.

## Test Signals

Tests cover external binary round trips for S3 and hinted RustFS tiers, legacy JSON decode fallback, and not-initialized save error formatting.
