# sources/storage-engines/tikv/components/batch-system/tests/cases/batch.rs

## Purpose
Integration-style tests for batch-system execution, priority routing, and resource-group scheduling.

## APIs, Types, And Functions
Defines `test_batch`, `test_priority`, and `test_resource_group`. Uses `Runner`, `Builder`, `BasicMailbox`, `Router`, `Config`, and `ResourceGroupManager`.

## Control Flow
`test_batch` sends a control callback that registers a normal FSM, then sends a normal callback and verifies handler metrics. `test_priority` registers normal and low-priority runners and asserts they are handled by matching-priority handlers. `test_resource_group` blocks the single poller, queues messages for two resource groups, releases the block, and expects the group with more tokens to run first.

## State And Persistence
State is confined to test channels, resource manager configuration, and running worker threads. No persistence.

## Dependencies And Integration Points
Exercises the public crate API and `kvproto::resource_manager` group settings. It validates integration between resource-control channels and scheduler message charging.

## Risks And Test Signals
These are strong signals for scheduler correctness beyond simple routing. Timing sleeps and blocking channels introduce some test sensitivity, but the assertions cover essential behavior expected by production raftstore/apply users.
