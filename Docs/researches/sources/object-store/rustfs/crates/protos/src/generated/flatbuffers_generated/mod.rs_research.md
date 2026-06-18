# sources/object-store/rustfs/crates/protos/src/generated/flatbuffers_generated/mod.rs

## Purpose

This generated-module wrapper exposes the FlatBuffers-generated Rust code below `flatbuffers_generated`. Its only item is `pub mod models;`, which makes the generated `models.rs` module available to the parent generated module.

## Important APIs, types, and functions

- `pub mod models;` declares and publicly exposes `flatbuffers_generated::models`.
- There are no functions, structs, constants, or state in this file.

## Control flow

The file has no runtime control flow. Cargo/Rust module resolution loads `models.rs` when this module is referenced.

## State and persistence behavior

There is no state or persistence. It is a compile-time namespace bridge.

## Dependencies and integration points

The module is consumed by `sources/object-store/rustfs/crates/protos/src/generated/mod.rs`, which declares `mod flatbuffers_generated;` and re-exports `flatbuffers_generated::models::*`. This means changing visibility or module names here directly affects the public generated API of `rustfs-protos`.

## Risks and edge cases

- Because this is generated-wrapper code, manual edits may be overwritten by the FlatBuffers generation pipeline.
- Removing `pub` would break the parent module's re-export path.
- Adding additional generated schemas here requires keeping parent re-exports and file generation in sync.

## Test signals

Compilation of `rustfs-protos` is the primary signal. Any consumer importing `rustfs_protos::generated::PingBody` through the parent re-export indirectly depends on this module declaration.
