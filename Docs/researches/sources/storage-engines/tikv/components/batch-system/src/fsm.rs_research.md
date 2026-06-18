# sources/storage-engines/tikv/components/batch-system/src/fsm.rs

## Purpose
Defines the finite-state-machine abstraction, scheduler abstraction, priorities, and atomic ownership holder used by mailboxes and pollers.

## APIs, Types, And Functions
`Priority` is `Low` or `Normal`. `FsmScheduler` schedules boxed FSMs, shuts down its resources, and can charge message resource usage. `Fsm` defines message type, metrics label, stopped status, optional mailbox attach/take, and priority. `FsmState<N>` owns an FSM pointer and tracks states `NOTIFIED`, `IDLE`, and `DROP`.

## Control Flow
`FsmState::take_fsm` atomically transitions IDLE to NOTIFIED and extracts the boxed FSM. `notify` takes the FSM, installs the mailbox, and schedules it. `release` returns an FSM to IDLE unless the state was concurrently marked DROP, in which case the FSM is dropped. `clear` marks DROP and drops any idle FSM.

## State And Persistence
State is in-memory and intentionally low-level: an `AtomicUsize` status, an `AtomicPtr`, and shared state count. No persistence exists. The unsafe pointer ownership is guarded by atomic state transitions.

## Dependencies And Integration Points
Integrated by `BasicMailbox`, `Router`, and schedulers. Messages must implement `ResourceMetered` so resource control can be charged before scheduling.

## Risks And Test Signals
The main risk is status/data inconsistency causing double free, leak, or panic. The implementation panics on invalid release states, making bugs visible. Router tests indirectly validate drop counts and mailbox cleanup via `state_cnt`.
