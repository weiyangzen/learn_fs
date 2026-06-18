# sources/object-store/rustfs/crates/targets/src/runtime/ops_diagnostics.rs

## Purpose
Registry for ops-diagnostics extensions. It validates extension schemas/contracts, records which diagnostic surfaces each extension serves, and authorizes read-only diagnostic access.

## Important APIs, types, and functions
- `OpsDiagnosticsRegistryError` reports invalid contracts, unsupported extension kinds, and missing required capability.
- `OpsDiagnosticsRegistration` records extension id and diagnostic surface.
- `OpsDiagnosticsRegistry` stores registrations by `OpsDiagnosticSurface`.
- `OpsDiagnosticsReadRequest` carries requested surface, capability, and admin authorization flag.
- `OpsDiagnosticsAccessDecision` returns allow or specific denial reasons.

## Control flow
`register_schema` rejects non-ops-diagnostics schemas, requires the ops diagnostics capability, validates the contract, then registers every declared surface. `authorize_read` denies unknown surfaces first, then missing admin authorization, then wrong capability, otherwise allowing read-only access.

## State and persistence behavior
Registrations are in-memory `BTreeMap` entries. The registry does not execute diagnostics or persist access decisions.

## Dependencies and integration points
It integrates with `rustfs_extension_schema` contracts, extension kinds, capabilities, and diagnostic surface enums. Builtin extension schema/contract constructors are re-exported from the crate root and used by tests.

## Risks and edge cases
Authorization is registry-local and assumes the caller has already performed any identity/authentication work that sets `admin_action_authorized`. Capability comparison is string-based. Registration allows multiple extensions per surface and does not deduplicate extension ids.

## Test signals
Tests verify default unknown-surface denial, successful builtin registration, read-only authorization, wrong capability denial, missing admin-action denial, rejection of non-diagnostics schemas, and rejection of contracts that mutate object data.
