<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/queue.go -->
# sources/storage-engines/pebble/cmd/pebble/queue.go

## Purpose
Provides shared flag binding for queue-style benchmark configuration used by the tombstone workload.

## Important APIs, Types, and Functions
`initQueue(cmd *cobra.Command, cfg *bench.QueueConfig)` binds `--queue-size` and `--queue-values` to a command.

## Control Flow
The helper is called during command initialization, notably from `tombstone.go`, and mutates the target command's flag set.

## State and Persistence Behavior
Only command/config state is changed. The queue workload's database mutations are implemented in the `bench` package.

## Dependencies and Integration Points
Depends on Cobra and `bench.QueueConfig`. Integrates with `bench.RunTombstone` through `tombstoneConfig.Queue`.

## Risks and Edge Cases
The helper assumes `cfg.Values` is a non-nil flag value. Reusing it on a command with already-defined flag names would produce Cobra flag conflicts.

## Test Signals
No direct tests. Signals are successful parsing of queue size/value distributions and their effect on tombstone benchmark workload shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cmd/pebble/queue.go -->
