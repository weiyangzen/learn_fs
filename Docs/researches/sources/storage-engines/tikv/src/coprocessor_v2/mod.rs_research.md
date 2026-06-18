# sources/storage-engines/tikv/src/coprocessor_v2/mod.rs

## Purpose
Documents and wires TiKV's v2 plugin-based coprocessor framework.

## Important APIs, Types, and Functions
Declares private modules `config`, `endpoint`, `plugin_registry`, and `raw_storage_impl`; publicly re-exports `Config` and `Endpoint`.

## Control Flow
No runtime control flow exists in this module root. It establishes compile-time visibility and public API boundaries.

## State and Persistence Behavior
No local state. Child modules manage dynamic plugin state, filesystem watching, and raw storage access.

## Dependencies and Integration Points
The module-level docs describe the framework as distinct from the legacy fixed-function coprocessor and inspired by HBase/BigTable coprocessors. Public re-exports are consumed by server/config layers that instantiate the v2 endpoint.

## Risks and Edge Cases
Keeping `plugin_registry` and `raw_storage_impl` private limits external coupling. Changing re-exports would alter the public crate API.

## Test Signals
No tests here; coverage comes from child modules.
