# sources/object-store/rustfs/crates/audit/tests/pipeline_layer_test.rs

## Purpose
This test file validates the audit pipeline/runtime abstraction layer around `AuditRegistry`: read-only runtime views, empty metric/health snapshots, replay worker stopping, empty activation, upsert/remove behavior, and replacement of runtime target sets.

## Important APIs, Types, and Functions
The tests use `AuditPipeline`, `AuditRegistry`, `AuditRuntimeFacade`, `AuditRuntimeView`, `ReplayWorkerManager`, `RuntimeActivation`, and the generic `rustfs_targets::Target` trait. A local `TestTarget` implements `Target<E>` with counters for `init` and `close`, plus no-op save/store methods.

## Control Flow
Empty registry tests assert list/get/snapshot APIs return empty values. Facade tests verify stopping replay workers is safe when none exist and activation of an empty list yields no targets/workers. Upsert tests call `AuditRuntimeView::upsert_target`, expect target initialization, list the canonical id, then remove and expect close. Replacement tests pass a `RuntimeActivation` containing one shared target and an empty replay manager, then confirm the registry and replay worker lock reflect the new state.

## State and Persistence Behavior
All state is held in `Arc<Mutex<AuditRegistry>>` and `Arc<RwLock<ReplayWorkerManager>>`. The local target has atomic counters, no persistent store, and always reports enabled/active.

## Dependencies and Integration Points
These tests are the most direct contract for `AuditRuntimeView`, `AuditRuntimeFacade`, and `AuditPipeline`, which are used by `AuditSystem` for target mutation, dispatch snapshots, replay activation, and runtime replacement.

## Risks and Edge Cases
The local target's id string must match runtime expectations (`primary:webhook`). Tests do not exercise failure from `init`, `close`, target stores, or replay workers, so error-path coverage is elsewhere or missing. Since the test target is generic over event type, trait bound changes in `rustfs_targets::Target` can break this file.

## Test Signals
Signals include safe empty operations, empty runtime snapshot behavior, upsert calling `init` exactly once, remove calling `close` exactly once, and facade replacement committing shared targets plus replay worker state.
