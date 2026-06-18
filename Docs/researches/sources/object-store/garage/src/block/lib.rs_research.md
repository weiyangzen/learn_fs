# sources/object-store/garage/src/block/lib.rs

Purpose: crate root for `garage_block`; wires modules and exposes the limited public surface needed by other Garage crates.

Important APIs/types/functions: public modules `manager`, `repair`, and `resync`; private modules `block`, `layout`, `metrics`, and `rc`; public re-exports `zstd_encode` and `CalculateRefcount`.

Control flow: no runtime logic. Module visibility intentionally keeps low-level block layout/metrics/reference-count internals crate-private.

State and persistence: none directly; persistence is delegated to module implementations.

Dependencies and integration points: imports tracing macros globally. Other crates typically interact through `manager::BlockManager`, repair/resync worker types, and `CalculateRefcount` callbacks.

Risks: re-export choices define crate boundary. Making internals public would increase compatibility burden; removing current re-exports can break model/admin integration.

Test signals: compile-time module linkage is the main signal.
