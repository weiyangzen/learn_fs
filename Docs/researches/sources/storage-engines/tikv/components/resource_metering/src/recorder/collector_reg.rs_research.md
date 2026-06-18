# sources/storage-engines/tikv/components/resource_metering/src/recorder/collector_reg.rs

## Purpose
`collector_reg.rs` implements registration and RAII deregistration of resource-metering collectors with the recorder worker.

## Important APIs, Types, And Functions
`CollectorRegHandle` wraps a `Scheduler<Task>`. `register` assigns a monotonically increasing `CollectorId`, schedules `Task::CollectorReg(CollectorReg::Register { ... })`, and returns a `CollectorGuard`. `new_for_test` builds a mock worker scheduler. `CollectorReg` is the recorder task payload for register/deregister operations. `CollectorGuard::drop` schedules deregistration if registration scheduling succeeded.

## Control Flow
Clients call `register(Box<dyn Collector>, as_observer)`. Non-observer collectors keep the recorder enabled, while observer collectors do not affect enabled state. When the guard is dropped, the recorder receives a deregister task for the same ID.

## State And Persistence Behavior
Collector IDs come from a static `AtomicU64` with sequential consistency. Guard state is just the ID and optional scheduler. Registration state itself lives in the recorder worker, not in this file.

## Dependencies And Integration Points
The file depends on `tikv_util::worker::{Scheduler, Worker}`, logging via `warn`, the `Collector` trait, and recorder `Task`. It is re-exported from `lib.rs` for external collector registration.

## Risks
If scheduling the register task fails, the returned guard has no scheduler and cannot deregister anything. Deregistration errors are logged only. ID allocation is process-local and monotonic; wraparound is theoretically possible but unrealistic.

## Test Signals
No local tests, but `new_for_test` supports recorder tests and integration tests around collector registration.
