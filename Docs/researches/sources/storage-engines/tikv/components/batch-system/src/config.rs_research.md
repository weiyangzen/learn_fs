# sources/storage-engines/tikv/components/batch-system/src/config.rs

## Purpose
Defines online-configurable parameters for the batch system worker pool.

## APIs, Types, And Functions
`Config` includes `max_batch_size`, `pool_size`, `reschedule_duration`, and `low_priority_pool_size`. `max_batch_size()` returns the configured size or the test/default fallback of 256. `Default` uses pool size 2, reschedule duration 5s, and one low-priority worker.

## Control Flow
The batch system consumes `Config` during `create_system` and poller construction. `PollHandler::begin` receives an update callback so online config can refresh max batch size between rounds. `reschedule_duration` and low-priority pool size are skipped for online config.

## State And Persistence
The struct is serializable/deserializable and may be persisted in TiKV config files by surrounding systems. Runtime copies are immutable except online config refresh points.

## Dependencies And Integration Points
Uses `online_config::OnlineConfig`, serde, and `ReadableDuration`. Integrated directly by `batch.rs`.

## Risks And Test Signals
The fallback max batch size exists because tests may bypass validation. Misconfigured pool sizes affect throughput and fairness; reschedule duration changes hot-FSM redistribution.
