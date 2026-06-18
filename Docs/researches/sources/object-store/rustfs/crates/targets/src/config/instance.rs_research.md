# sources/object-store/rustfs/crates/targets/src/config/instance.rs

## Purpose
Canonical normalization layer for target plugin instances. It turns legacy file/env target configuration into `TargetPluginInstanceRecord` values that carry domain, plugin identity, instance id, enablement, source provenance hints, and effective merged config.

## Important APIs, types, and functions
- `TargetPluginInstanceCompatDescriptor` describes one legacy target family: domain, plugin id, target type, config subsystem, route prefix, and valid fields.
- `TargetInstanceSourceHints` records whether default and instance config came from files or environment, and classifies records as `Config`, `Env`, or `Mixed`.
- `TargetPluginInstanceRecord` is the normalized instance model consumed by compatibility/admin surfaces.
- `normalize_target_plugin_instances_from_env` delegates merging to `collect_merged_target_configs_from_env`, then enriches each merged record with descriptor metadata.
- `normalize_legacy_target_instances*` are compatibility aliases around the canonical normalization functions.

## Control flow
The function builds a valid-field set from the descriptor, collects merged configs for the descriptor subsystem and route prefix, then maps every merged record into a plugin instance record. Disabled instances are preserved in this layer, unlike `collect_target_configs`, so admin surfaces can report disabled definitions.

## State and persistence behavior
The module is read-only. It materializes effective configs from in-memory `Config` plus environment variables and preserves source hints that explain whether the materialized value came from file defaults, file instance entries, env defaults, or env instance entries.

## Dependencies and integration points
It bridges `rustfs_config::server_config::Config/KVS`, `TargetDomain`, builtin manifests, and `loader.rs`. Higher-level control/admin code can use records to present plugin instances without knowing legacy subsystem naming rules.

## Risks and edge cases
Default-only entries are intentionally excluded by the loader, so a globally enabled default target does not create an instance without file or env instance material. Environment-only instances need an explicit instance `enable` flag to be discovered. Mixed-source classification can surprise callers because a default from one source plus an instance from another source produces `Mixed`.

## Test signals
Tests verify notify and audit webhook normalization, domain/subsystem preservation, disabled instance retention, default-only exclusion, mixed source hints, and compatibility wrapper equivalence.
