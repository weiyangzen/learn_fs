# sources/storage-engines/tikv/components/batch-system/src/scheduler.rs

## Purpose
Implements concrete schedulers that enqueue normal and control FSMs into poller channels.

## APIs, Types, And Functions
`NormalScheduler<N,C>` holds normal and low-priority resource-control senders. `ControlScheduler<N,C>` holds the normal-priority sender for control FSMs. Both implement `Clone` and `FsmScheduler`.

## Control Flow
Normal scheduling checks `fsm.get_priority()` and sends `FsmTypes::Normal` with a coarse schedule timestamp to the matching queue. Control scheduling sends `FsmTypes::Control`. Shutdown sends 256 `FsmTypes::Empty` sentinels to wake pollers because explicit channel close is not available. Normal message resource consumption delegates to the resource-control sender; control messages are not charged here.

## State And Persistence
Schedulers only hold channel handles. Schedule timestamps become metric input when `Batch::push` observes wait duration.

## Dependencies And Integration Points
Uses `resource_control::channel::Sender`, crossbeam `SendError`, TiKV time utilities, and `FsmTypes`. Constructed by `create_system` and stored by `Router`.

## Risks And Test Signals
The magic shutdown count assumes it exceeds possible poller count. Failed sends are logged but not retried. Priority routing is covered by `test_priority`, and resource charging is covered by `test_resource_group`.
