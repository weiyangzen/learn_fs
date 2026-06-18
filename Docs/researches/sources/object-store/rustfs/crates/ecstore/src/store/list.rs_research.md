# sources/object-store/rustfs/crates/ecstore/src/store/list.rs

## Purpose
This file is a thin `ECStore` list/walk façade. It exposes store-level handler methods for S3 object listing, object version listing, and internal walking, forwarding requests to lower-level internal implementations while keeping the public handler surface in the `store` module cohesive.

## Important APIs, Types, And Functions
- `handle_list_objects_v2(self: Arc<Self>, ...) -> Result<ListObjectsV2Info>` delegates to `inner_list_objects_v2`.
- `handle_list_object_versions(self: Arc<Self>, ...) -> Result<ListObjectVersionsInfo>` delegates to `inner_list_object_versions`.
- `handle_walk(self: Arc<Self>, rx, bucket, prefix, result, opts) -> Result<()>` delegates to `walk_internal`.
- The handlers traffic in `ListObjectsV2Info`, `ListObjectVersionsInfo`, `ObjectInfoOrErr`, `WalkOptions`, and `CancellationToken` from surrounding modules.

## Control Flow
There is no additional branching or storage selection logic here. Each handler is instrumented where appropriate and immediately awaits its corresponding inner operation with the same arguments. `handle_walk` passes the cancellation token and result channel through so the underlying walker owns traversal and streaming.

## State And Persistence Behavior
This file does not mutate persistent state directly. Listing and walking behavior, metadata reads, version selection, cache usage, and object emission are all controlled by the delegated inner implementations. Its state impact is limited to async call boundaries and tracing spans.

## Dependencies And Integration Points
The module depends entirely on `super::*` for `ECStore`, result types, options, and inner methods. It integrates the object-store API layer with the internal list/walk engines and likely participates in trait implementations or higher-level S3 handlers through `ECStore` methods.

## Risks And Edge Cases
- Because this is a pass-through layer, most correctness risks live in the inner methods. The local risk is argument drift if handler signatures evolve independently from inner functions.
- `fetch_owner`, delete inclusion, continuation markers, version markers, and delimiters are all passed through without validation here; validation must be enforced downstream.
- `handle_walk` relies on the downstream implementation to honor cancellation and handle backpressure on the `mpsc::Sender`.

## Test Signals
No tests are defined in this file. Coverage must come from tests of `inner_list_objects_v2`, `inner_list_object_versions`, `walk_internal`, or higher-level S3 list/walk API tests. A simple delegation unit test would have little value unless mocks are introduced; integration tests should verify marker/delimiter/version behavior.
