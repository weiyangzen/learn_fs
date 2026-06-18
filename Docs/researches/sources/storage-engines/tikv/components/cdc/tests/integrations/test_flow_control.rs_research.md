# sources/storage-engines/tikv/components/cdc/tests/integrations/test_flow_control.rs

## Purpose
This integration test verifies CDC flow control when the endpoint's memory quota is too small for a pending event. It proves normal events are delivered while under quota, oversized events produce a congested error, and the affected region delegate is removed.

## Important APIs, Types, And Functions
The test uses `TestSuiteBuilder::memory_quota`, `new_event_feed`, `Task::Validate`, `Validate::Region`, `MemoryQuota` indirectly through the CDC service, and transactional KV RPC helpers from `TestSuite`. The event assertions inspect `Event_oneof_event::Entries`, `Event_oneof_event::Error`, `EventLogType::Initialized`, `EventLogType::Prewrite`, and the `congested` error field.

## Control Flow
`test_cdc_congest` starts a single-node server cluster with a 1 KiB CDC memory quota and subscribes to region 1. It first receives the mandatory `Initialized` event. It then prewrites a value of half the quota and expects a normal `Prewrite` row. A second prewrite with a value twice the quota is expected to return one CDC error event with `has_congested()`. Finally it schedules `Validate::Region` and checks the delegate is gone.

## State And Persistence Behavior
The test writes MVCC locks through real prewrite RPCs. The key persistent signal is not the written data itself but the CDC endpoint's memory-accounted event path: under-quota events remain deliverable, while an over-quota event causes endpoint-side subscription cleanup. The delegate removal is checked through endpoint scheduler state.

## Dependencies And Integration Points
It depends on the same simulated Raftstore and CDC gRPC service setup as the rest of the CDC tests. `configure_for_lease_read` is used to make timing reliable. The test integrates CDC txn-extra scheduling, memory quota enforcement, gRPC event delivery, and internal endpoint validation.

## Risks
The test assumes the encoded CDC prewrite event size tracks the chosen value size closely enough that half quota succeeds and double quota fails. Changes in event overhead, memory accounting, or quota semantics could make the threshold brittle. The delegate cleanup assertion is asynchronous and guarded by a one-second channel timeout.

## Test Signals
A passing run signals that CDC still sends `Initialized`, still allows normal prewrite delivery below quota, converts congestion to a structured CDC congested error, and removes the region delegate after congestion.
