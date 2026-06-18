# sources/storage-engines/tikv/components/cdc/src/config.rs

## Purpose
Provides an online config manager adapter for CDC.

## APIs, Types, And Functions
`CdcConfigManager(pub Scheduler<Task>)` implements `online_config::ConfigManager`. `dispatch` schedules `Task::ChangeConfig(change)` on the CDC worker scheduler. `Deref` exposes the underlying `Scheduler<Task>`.

## Control Flow
When online config changes arrive, the config framework calls `dispatch`; CDC handles the change asynchronously as a worker task rather than applying it in the config callback thread.

## State And Persistence
The manager stores only a scheduler handle. Actual config state and persistence live in the broader TiKV online config system and CDC task handler.

## Dependencies And Integration Points
Uses `online_config::{ConfigChange, ConfigManager}`, TiKV worker `Scheduler`, and crate-level `Task`. It bridges config infrastructure to CDC's internal task loop.

## Risks And Test Signals
Scheduling errors propagate as boxed errors. The main risk is delayed or failed application if the CDC scheduler is stopped or congested. This small adapter has no local tests in the file; coverage likely comes from CDC integration tests.
