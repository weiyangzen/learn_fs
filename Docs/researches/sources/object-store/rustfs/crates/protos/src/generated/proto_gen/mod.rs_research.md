# sources/object-store/rustfs/crates/protos/src/generated/proto_gen/mod.rs

## Purpose

This generated protobuf namespace wrapper exposes the generated `node_service` module. It is the protobuf/gRPC counterpart to the FlatBuffers wrapper under `flatbuffers_generated`.

## Important APIs, types, and functions

- `pub mod node_service;` declares and publicly exposes generated code from `node_service.rs`.
- The file itself defines no functions, structs, constants, or state.

## Control flow

There is no runtime control flow. Rust module resolution includes `node_service.rs` when `proto_gen::node_service` is referenced.

## State and persistence behavior

There is no state or persistence in this wrapper. State and wire-format behavior live in the generated protobuf service/client/message code in `node_service.rs`.

## Dependencies and integration points

The module is exposed by `generated/mod.rs` as `pub mod proto_gen`, so consumers use paths such as `rustfs_protos::generated::proto_gen::node_service`. The underlying generated service code depends on `prost`, `tonic`, and `tonic-prost` according to the crate manifest.

## Risks and edge cases

- Adding or renaming protobuf files requires updating this generated wrapper or regenerating it.
- Since this is a namespace bridge, a missing `node_service.rs` or stale generated file breaks the entire protobuf public surface.
- Manual edits may be overwritten by the protobuf generation pipeline.

## Test signals

The key signal is `cargo check -p rustfs-protos`, plus any integration test that imports generated node service clients, servers, and messages through `generated::proto_gen::node_service`.
