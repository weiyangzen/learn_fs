# sources/storage-engines/tikv/components/tidb_query_datatype/src/lib.rs

## Purpose
This is the crate root for `tidb_query_datatype`, which houses shared datatype, codec, builder, and expression context code used by TiKV query crates.

## Important APIs, types, and functions
The crate enables several nightly features (`proc_macro_hygiene`, `min_specialization`, `test`, `str_internals`, `core_intrinsics`, and `bool_to_result`) and imports project macros from `num_derive`, `static_assertions`, `tikv_util`, and `bitflags`. Public modules are `builder`, `def`, `error`, `codec`, and `expr`. The crate prelude currently re-exports `FieldTypeAccessor`, and the root re-exports `def::*` and `error::*`.

## Control flow
There is no runtime control flow; this file controls compilation, macro availability, module visibility, and public exports.

## State and persistence behavior
No state is stored here.

## Dependencies and integration points
This root is consumed by query expression, aggregation, and executor crates. Its exported APIs are the shared vocabulary for field metadata, eval type conversion, row codecs, MySQL datatypes, and evaluation contexts.

## Risks and edge cases
The crate depends on nightly/internal features, so compiler upgrades can affect it. Macro imports are crate-wide and can hide where helper macros originate. Public re-exports mean changes to `def` or `error` can become semver-visible inside the workspace.

## Test signals
The root conditionally imports the `test` crate for test builds. Behavioral coverage is in the public modules.
