# sources/sync-backup/syncthing/internal/db/counts.go

## Purpose
This file defines the aggregate count structure used by database implementations and callers to summarize folder/file state.

## Important APIs, Control Flow, And State
`Counts` stores item counts by type (`Files`, `Directories`, `Symlinks`, `Deleted`), byte totals, sequence, associated device ID, and local flag bucket. `Add` returns a combined count, sums sequences, resets `DeviceID` to `protocol.EmptyDeviceID`, and ORs local flags. `TotalItems` sums all item count classes. `String` renders a diagnostic summary with decoded local flag names and the raw flag value. `Equal` compares only numeric counts and bytes, deliberately ignoring sequence, device, and flags.

## Dependencies And Integration Points
It depends on `lib/protocol` for device IDs and local flags. It is returned by the database interface and used by GUI/API model summaries, folder status logic, and validation/debug paths.

## Risks And Test Signals
`Add` summing `Sequence` is useful for aggregate arithmetic but may not represent a meaningful database sequence for mixed devices. `String` appends raw flags whenever any flag is set, including known flags, which is diagnostic rather than stable UI output. Tests should verify arithmetic, `Equal` semantics, and flag rendering for each local flag.
