# sources/storage-engines/tikv/components/batch-system/src/lib.rs

## Purpose
Crate root for the batch-system component. It declares modules and re-exports the public API used by TiKV subsystems and tests.

## APIs, Types, And Functions
Exports `BatchRouter`, `BatchSystem`, `FsmTypes`, `HandleResult`, `HandlerBuilder`, `PollHandler`, `Poller`, `PoolState`, `create_system`, `Config`, `Fsm`, `FsmScheduler`, `Priority`, `BasicMailbox`, `Mailbox`, `FsmType`, and `Router`. The optional `test_runner` module is public only when the feature is enabled.

## Control Flow
No runtime control flow exists in this file. It controls module visibility and public API shape.

## State And Persistence
No state is stored here.

## Dependencies And Integration Points
Acts as the integration boundary for users of the crate, hiding internal module paths while preserving access to core traits and constructors.

## Risks And Test Signals
Changing re-exports is a compatibility risk for all TiKV components using `batch_system::*`. Tests and benches rely on the exported `test_runner` and core types.
