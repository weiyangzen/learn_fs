# sources/object-store/rustfs/crates/targets/src/catalog/mod.rs

## Purpose
Catalog module root plus an example installable external webhook sidecar plugin. It exposes built-in and extension catalog submodules and provides a fully populated example manifest/installation/runtime tuple for tests and documentation-like usage.

## Important APIs and Types
`ExampleInstallableTargetPlugin` groups a `TargetPluginMarketplaceManifest`, `TargetPluginInstallation`, `SidecarPluginRuntime`, and valid field names. `example_external_webhook_plugin` builds a `TargetPluginManifest` for `external:webhook-sidecar`, wraps it with an installable marketplace manifest and distribution artifact metadata, constructs a sidecar handshake with health/send/shutdown capabilities, creates a `SidecarPluginRuntime`, enables it with verified external policy/safety checks, and returns installation metadata marked installed.

## Control Flow and State
The function is deterministic except for no external I/O; it constructs in-memory metadata only. The hard-coded `last_verified` timestamp is `"2026-05-13T20:00:00Z"`.

## Integration Points
Uses control-plane installation helpers, target domain and manifest types, sidecar runtime policy and protocol types, and is consumed by `catalog/extension.rs` tests to verify external manifest mapping.

## Risks
The example includes placeholder URLs and digest/signature/provenance values; it must not be treated as a real install source. Hard-coded policy values and timestamp can become stale as protocol versions evolve. Because tests rely on this example, changes to sidecar safety policy validation may require updates here.

## Test Signals
A unit test verifies plugin id, installed state, healthy runtime, and valid field list. Extension catalog tests also consume this example to verify sidecar mapping and disabled-by-default behavior.
