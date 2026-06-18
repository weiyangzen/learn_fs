# sources/object-store/minio/cmd/rebalstatus_string.go

## Purpose
This generated file provides string names for the `rebalStatus` enum used in rebalance metadata and admin status.

## Important APIs, Types, and Functions
The generated `_` function checks enum ordinal stability. `_rebalStatus_name`, `_rebalStatus_index`, and `func (i rebalStatus) String() string` map statuses to names: `None`, `Started`, `Completed`, `Stopped`, and `Failed`.

## Control Flow and State
There is no mutable state. Out-of-range statuses are formatted as `rebalStatus(<n>)`.

## Dependencies and Integration Points
`rebalance-admin.go` uses `ps.Info.Status.String()` to expose status text to admin clients.

## Risks and Test Signals
Stale generation is the main risk and is caught at compile time if enum values change. Behavioral tests should focus on rebalance admin output rather than this generated helper.
