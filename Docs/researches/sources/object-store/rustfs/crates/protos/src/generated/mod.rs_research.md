# sources/object-store/rustfs/crates/protos/src/generated/mod.rs

## Purpose

This generated top-level module wires together the prost/tonic generated gRPC modules and the FlatBuffers generated modules for the `rustfs-protos` crate. It centralizes generated-code lint suppression and re-exports FlatBuffers model types.

## Important APIs, types, and functions

- `#![allow(unused_imports)]` and `#![allow(clippy::all)]` suppress warnings commonly emitted by generated code.
- `pub mod proto_gen;` exposes generated protobuf/gRPC modules.
- `mod flatbuffers_generated;` keeps the FlatBuffers wrapper module private at this level.
- `pub use flatbuffers_generated::models::*;` re-exports generated FlatBuffers model items such as `PingBody`.

## Control flow

There is no runtime control flow. Rust module loading and public re-export resolution determine which generated types are available to users of the crate.

## State and persistence behavior

There is no state or persistence. The file establishes namespace and visibility for generated protocol definitions.

## Dependencies and integration points

This module integrates `proto_gen/mod.rs`, which currently exposes `node_service`, with the FlatBuffers `models` namespace. Consumers can import protobuf service modules through `generated::proto_gen::...` and FlatBuffers model types directly through `generated::*`. The lint allowances protect generated files from breaking workspace-wide clippy checks.

## Risks and edge cases

- Glob re-export of FlatBuffers models can create name collisions as schemas grow.
- Keeping `flatbuffers_generated` private while re-exporting its contents is convenient, but downstream users cannot address the original generated namespace path through this module.
- `allow(clippy::all)` is appropriate for generated code but can mask issues if hand-written code is later added to this module.
- Changes to this module are public API changes for consumers of `rustfs-protos`.

## Test signals

Compilation is the main signal. Public API tests or downstream compile tests should verify both `generated::proto_gen::node_service` access and direct import of re-exported FlatBuffers models.
