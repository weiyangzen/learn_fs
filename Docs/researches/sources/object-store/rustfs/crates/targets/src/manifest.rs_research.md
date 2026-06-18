# sources/object-store/rustfs/crates/targets/src/manifest.rs

## Purpose
Defines declarative manifest metadata for builtin and future installable target plugins, including supported domains, secret fields, packaging, entrypoint style, runtime transport, and distribution artifacts.

## Important APIs, types, and functions
- Core structs: `TargetPluginManifest`, `TargetPluginMarketplaceManifest`, `TargetPluginExternalRuntimeContract`, `TargetPluginArtifactManifest`, and `TargetPluginDistributionManifest`.
- Enums: `TargetPluginPackaging`, `TargetPluginEntrypointKind`, and `TargetPluginRuntimeTransport`.
- Constructors: `builtin_target_manifest`, `builtin_target_marketplace_manifest`, and `installable_target_marketplace_manifest`.
- `impl From<TargetPluginManifest> for TargetPluginMarketplaceManifest` turns builtins into marketplace records with builtin packaging and in-process runtime transport.

## Control flow
`builtin_target_manifest` matches target type strings to display names, builtin plugin ids, and secret-field lists. Marketplace conversion fills stable API/runtime compatibility versions and uses `None` distribution for builtins. Installable manifests preserve base metadata but mark packaging external and attach a supplied runtime contract and distribution.

## State and persistence behavior
The module stores only static metadata. Secret-field arrays identify config keys that admin/UI layers should treat as sensitive; they do not themselves redact or persist values.

## Dependencies and integration points
It depends on `TargetDomain` and many `rustfs_config` field constants. Control-plane validation consumes marketplace manifests. Instance normalization and plugin descriptors use builtin plugin ids to identify target types consistently.

## Risks and edge cases
Unknown target types become `custom:target` with no secret fields, which could under-classify sensitive custom config if used beyond placeholder scenarios. Secret field lists must be updated whenever new credential-like keys are added. Builtin API compatibility strings are hard-coded constants and should be versioned deliberately.

## Test signals
Tests verify secret fields for webhook and Kafka, marketplace metadata derived from builtins, supported-domain preservation, stable builtin conversion, and an installable sidecar manifest carrying distribution metadata.
