# sources/object-store/rustfs/crates/targets/src/catalog/extension.rs

## Purpose
Builds extension-schema metadata for built-in target plugins, S3 post-auth hooks, and ops diagnostics. It maps target marketplace manifests and built-in capabilities into the shared `rustfs_extension_schema` contracts.

## Important APIs and Functions
Constants define API/capability names: `OPS_DIAGNOSTICS_EXTENSION_API_VERSION`, `S3_HOOK_EXTENSION_API_VERSION`, `TARGET_AUDIT_CAPABILITY`, and `TARGET_NOTIFY_CAPABILITY`.

`builtin_extension_schemas` combines target schemas, S3 hook schema, and ops diagnostics schema. `builtin_s3_hook_extension_schema` and `builtin_s3_hook_contract` describe a built-in post-auth hook registry that does not mutate object data or bypass IAM. `builtin_ops_diagnostics_extension_schema` and `builtin_ops_diagnostics_contract` expose metrics, trace, profile, health, and diagnostics surfaces requiring admin action.

`target_marketplace_extension_schema` maps `TargetPluginMarketplaceManifest` to `ExtensionSchema`, selecting runtime boundary, mapping supported domains to capabilities, and disabling external or boundary-required plugins by default. `builtin_target_extension_schemas` deduplicates built-in target types from audit and notify admin descriptors through a `BTreeMap`.

## Control Flow and State
Everything is pure vector/struct construction. Deduplication state is local to `builtin_target_extension_schemas`.

## Integration Points
Consumes built-in target admin descriptors, target domain and manifest types, and the extension schema crate's validation contracts. This file bridges target plugin metadata to a broader extension catalog.

## Risks
Capability ordering follows manifest `supported_domains`; consumers should not depend on more than documented order. Built-in target schemas depend on admin descriptors rather than runtime descriptors, so admin/runtime descriptor drift can affect catalog accuracy. External packaging is disabled by default even if entrypoint metadata says builtin, which is intentional but important.

## Test Signals
Unit tests validate builtin target marketplace mapping, external sidecar disabled mapping, external packaging disabled behavior, uniqueness and validation of nine built-in target schemas, combined catalog size of eleven, S3 post-auth hook contract semantics, and ops diagnostics admin/read-only semantics.
