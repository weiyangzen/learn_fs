# sources/storage-engines/tikv/components/backup-stream/src/metadata/mod.rs

## Purpose
`metadata/mod.rs` is the namespace root for backup stream metadata. It controls which metadata submodules are public and re-exports the high-level client types used by the rest of the crate.

## Important APIs, types, and functions
- Private modules: `checkpoint_cache`, `client`, and `metrics`.
- Public modules: `keys`, `store`, and `test`.
- Re-exports: `Checkpoint`, `CheckpointProvider`, `MetadataClient`, `MetadataEvent`, `PauseStatus`, and `StreamTask`.

## Control flow
There is no runtime control flow. The file defines compile-time module boundaries.

## State and persistence behavior
No state is held here; persistent metadata behavior lives in `client`, `keys`, and `store`.

## Dependencies and integration points
`Endpoint` imports the re-exported `MetadataClient`, `MetadataEvent`, `StreamTask`, and `store::MetaStore`. Integration tests can use `metadata::test` because that module is deliberately public under `cfg(test)` contents.

## Risks and edge cases
- `pub mod test` exists for integration-test ergonomics, but the file contents are guarded by `#![cfg(test)]`; changing this can break test-only consumers.
- Keeping `metrics` private centralizes metric use inside metadata, while making `keys` public exposes key layout helpers to other modules.

## Test signals
No direct tests. The metadata module tree is exercised by client, store, and endpoint-related tests.
