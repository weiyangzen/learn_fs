# sources/object-store/rustfs/crates/targets/src/config/mod.rs

## Purpose
Public facade for the target configuration subsystem. It keeps implementation modules private where possible and re-exports the normalization, loader, builder, and validator APIs used by the rest of `rustfs_targets`.

## Important APIs, types, and functions
- Private modules: `common`, `instance`, `loader`, and `target_args`.
- Re-exports instance descriptors and records such as `TargetPluginInstanceRecord`, source-hint types, and legacy compatibility aliases.
- Re-exports loader functions including `collect_target_configs*` and `collect_env_target_instance_ids*`.
- Re-exports per-target builders and validators for AMQP, Kafka, MQTT, MySQL, NATS, PostgreSQL, Pulsar, Redis, and Webhook.

## Control flow
There is no runtime control flow beyond Rust module resolution. The file defines the crate-level import surface and intentionally hides shared helper details in private modules.

## State and persistence behavior
No state is stored. This module only controls API visibility.

## Dependencies and integration points
`lib.rs`, `plugin.rs`, admin handlers, and target initialization code import through this facade. Because it re-exports legacy and canonical names, it is also a compatibility boundary for callers that still use older target-instance terminology.

## Risks and edge cases
Accidental removal or renaming of re-exports is a breaking crate API change. Keeping `common` private means any validation helper needed outside the config subsystem must be intentionally promoted through this file or another public API.

## Test signals
No direct tests live in this file. Coverage comes from the re-exported modules' unit tests and downstream compilation of modules that import through `crate::config`.
