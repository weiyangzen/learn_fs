<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag.rs -->
# sources/object-store/rustfs/crates/rio/src/etag.rs

## Purpose
Provides tests and module documentation for the trait-based ETag resolution model used by `rio`. It validates that ETags can be found through nested reader wrappers such as compression, encryption, `HashReader`, and `EtagReader`.

## Important APIs, types, and functions
- Exercises `resolve_etag_generic`.
- Uses `EtagReader`, `HashReader`, `CompressReader`, and `EncryptReader` as representative wrappers.
- Relies on `EtagResolvable` delegation implementations from `lib.rs` and the reader modules.

## Control flow
The tests create direct and nested reader stacks, sometimes consume them to EOF, then call `resolve_etag_generic`. ETag-bearing wrappers return either a configured checksum or a finalized MD5. Transforming wrappers delegate resolution to their inner reader. Tests also cover `None` paths where no ETag is available.

## State and persistence behavior
No production state is defined in this file. The important state under test lives inside wrapped readers: `EtagReader` must finish before exposing calculated MD5 values, while `HashReader` can expose configured ETags when MD5 tracking is not disk-deferred.

## Dependencies and integration points
Depends on MD5 and hex encoding in tests, `rustfs_utils::compress::CompressionAlgorithm`, Tokio readers, and the local reader stack. It is a cross-module integration test for the capability traits exported by `rio`.

## Risks and edge cases
Because this file is test-only, regressions in ETag propagation would break object metadata/reporting without touching any production code here. The tests assume wrapper order does not obscure the inner capability; new wrappers must implement the delegation macros or ETag discovery will silently return `None`.

## Test signals
Signals include direct `EtagReader` resolution, `HashReader` resolution, single and double wrapper delegation, complex compression/encryption nesting, `HashReader` in nested structures, real-world simulated stacks, and explicit no-ETag scenarios.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/etag.rs -->
