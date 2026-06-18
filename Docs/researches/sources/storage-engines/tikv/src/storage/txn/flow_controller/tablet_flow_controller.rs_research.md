# sources/storage-engines/tikv/src/storage/txn/flow_controller/tablet_flow_controller.rs

## Purpose
`tablet_flow_controller.rs` adapts scheduler flow control to tabletized storage where each region can have its own engine instance and limiter. It preserves the singleton flow-checking logic per region while adding lifecycle management and a global pending-compaction discard controller.

## Important APIs, types, and functions
`TabletFlowFactorStore<EK>` wraps `TabletRegistry<EK>` and implements `FlowControlFactorStore` by querying the latest tablet for a region. `TabletFlowController` owns a control channel, dispatcher thread, `Limiters` map from region ID to `(Limiter, discard_ratio)`, a `global_discard_ratio`, and config tracker. `FlowInfoDispatcher` owns the background event loop. `CompactionPendingBytesChecker` aggregates per-region pending bytes by CF and feeds a global `FlowChecker`.

## Control flow
`TabletFlowController::new` creates the shared maps and starts the dispatcher. The dispatcher receives flow-control messages and `FlowInfo`. L0, L0Intra, and Flush events are routed only to an existing region checker. Compaction events update the region checker, report the current pending bytes to the global checker, and recompute global pending-byte discard ratio. Created events insert or reference-count a region `FlowChecker`, creating a limiter and per-region discard ratio if needed. Destroyed events decrement the checker reference count, remove the checker and limiter when it reaches zero, and remove that region's pending-byte contribution.

Read-side APIs look up the region limiter under an `RwLock`. Unknown regions are unlimited and never dropped. `should_drop` uses the maximum of the region discard ratio and global discard ratio.

## State and persistence behavior
State is in memory: per-region limiters, per-region atomic discard ratios, checker reference counts, global discard ratio, pending-byte aggregation, online config, and background thread lifecycle. No persistent data is modified. Region/tablet existence comes from `TabletRegistry`, but this module only observes it.

## Dependencies and integration points
It depends on `TabletRegistry`, `FlowInfo`, `FlowChecker` from the singleton module, online config, limiter utilities, and scheduler metrics. It integrates storage tablet lifecycle events with scheduler flow control and lets the facade in `mod.rs` treat tablet mode like singleton mode.

## Risks
Lifecycle races are the main risk. Events for a region before `Created` or after `Destroyed` are ignored, which is safe but can miss pressure signals. Reference counts must match create/destroy events or limiters can leak or disappear too early. Pending-compaction aggregation must remove destroyed regions promptly or global discard ratio can stay high. The global checker uses region ID 0 and a dummy limiter, so only discard-ratio behavior should be relied on there.

## Test signals
Tests create a temporary tablet registry, load tablet contexts, and exercise basic facade behavior, create/destroy lifecycle including duplicate creates, memtable control, L0 control, and pending-compaction discard behavior. These tests reuse singleton helper assertions, which checks consistency across controller modes.
