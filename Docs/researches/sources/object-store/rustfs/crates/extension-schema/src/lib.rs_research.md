# sources/object-store/rustfs/crates/extension-schema/src/lib.rs

Purpose: defines serializable extension schema contracts and validators for RustFS extension kinds, runtime boundaries, S3 post-auth hooks, and ops diagnostics.

Important APIs/types/functions: constants `EXTENSION_SCHEMA_VERSION`, `OPS_DIAGNOSTICS_CAPABILITY`, and `S3_POST_AUTH_HOOK_CAPABILITY` anchor stable identifiers. `ExtensionKind`, `ExtensionRuntimeBoundary`, `ExtensionRuntimeContract`, `ExtensionCapabilityRef`, and `ExtensionSchema` define the top-level extension document. `S3HookPoint` and `S3HookContract` describe read-only post-auth S3 hook capabilities. `OpsDiagnosticSurface` and `OpsDiagnosticsContract` describe admin-gated operational diagnostic surfaces. Validation entry points are `validate_extension_schemas`, `validate_s3_hook_contract`, and `validate_ops_diagnostics_contract`; failures are typed as `ExtensionSchemaError` and `ExtensionContractError`.

Control flow: schema validation iterates all schemas, trims mandatory strings, checks the exact schema version, rejects empty or duplicate capabilities with `BTreeSet`, requires external `Sidecar`/`Wasm` boundaries to be disabled by default, and rejects duplicate extension IDs. S3 hook validation rejects empty/duplicate hook points, object data mutation, and IAM bypass. Ops diagnostics validation rejects empty/duplicate surfaces, object mutation, and missing admin-action requirement.

State and persistence: all contracts are `Serialize`/`Deserialize`; persistence is the JSON/config representation of extension declarations. There is no mutable global state. `#[serde(rename_all = "snake_case")]`, transparent capability refs, and `deny_unknown_fields` on contract bodies are important wire-shape controls.

Dependencies and integration: uses `serde`, `thiserror`, and `BTreeSet`. It integrates with extension discovery/config systems that need deterministic validation before enabling plugins or diagnostic surfaces.

Risks: `S3HookPoint::is_post_auth` currently always returns true, so adding non-post-auth variants would require updating this method. `ExtensionCapabilityRef::new` does not trim or validate until schema validation, so callers must run the validator. `ExtensionKind` is not cross-checked against declared capabilities/contracts in this file.

Test signals: unit tests lock JSON shape, valid ops diagnostics schemas, disabled-by-default external extensions, duplicate capability and extension ID rejection, schema-version rejection, empty capability rejection, S3 hook safety, duplicate hook rejection, and ops diagnostics admin/read-only requirements.
