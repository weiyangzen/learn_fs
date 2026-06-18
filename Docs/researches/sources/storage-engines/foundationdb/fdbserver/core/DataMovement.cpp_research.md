# sources/storage-engines/foundationdb/fdbserver/core/DataMovement.cpp

## Purpose
Maps `DataMovementReason` enum values to numeric priorities and back. This centralizes data-distribution reason priority ordering from server knobs.

## Important APIs, Types, and Functions
- `buildPriorityMappings()` initializes static reason-to-priority and priority-to-reason maps.
- `dataMovementPriority(DataMovementReason reason)` returns the configured priority for a reason.
- `priorityToDataMovementReason(int priority)` returns the reason associated with a priority.

## Control Flow
The first call builds static maps from enum constants and `SERVER_KNOBS` priority values. It then constructs the inverse map and asserts that every priority is unique. Public functions look up with `.at()`, so unknown reasons or priorities throw standard map lookup errors/assert in debug depending on context.

## State and Persistence Behavior
No durable state. Static in-process maps persist for the life of the process after first construction.

## Dependencies and Integration Points
Depends on `DataMovement.h` and server knobs. Used wherever data-distribution logic needs to compare, persist, or decode data movement priority/reason metadata.

## Risks and Edge Cases
Duplicate configured priorities are fatal via trace and assert. Because the maps are static, knob values must be finalized before first use; later knob mutation would not rebuild mappings. Sentinel reasons intentionally map to negative values.

## Test Signals
No embedded tests. Useful tests should verify one-to-one priority mappings for all enum values and fail on duplicate priorities.
