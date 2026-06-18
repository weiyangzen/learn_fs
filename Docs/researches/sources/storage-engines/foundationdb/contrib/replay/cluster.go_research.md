# sources/storage-engines/foundationdb/contrib/replay/cluster.go

## Purpose

`cluster.go` reconstructs a simplified FoundationDB simulation cluster topology from parsed trace events. It tracks workers, roles, data-center IDs, machine type classification, and role epochs so the replay TUI can display cluster state at a selected point in the trace.

## Important APIs, Types, and Functions

- `RoleInfo` stores role `Name`, role `ID`, and an optional `Epoch`/generation string.
- `Worker` stores `Machine`, assigned `Roles`, `MachineType` (`main`, `tester`, or `unknown`), and `DCID`.
- `ClusterState` is a map from machine address to `*Worker`.
- `NewClusterState()` initializes an empty state.
- `parseAddress(address string)` classifies FDB simulation-style addresses:
  - IPv6-ish `[abcd::X:Y:...]` where `X=2` is main and `X=3` is tester, while `Y` is DC ID.
  - IPv4-ish `X.Y...` with the same type/DC interpretation.
- `BuildClusterState(events []TraceEvent)` replays trace events into current worker-role state.
- `GetWorkersByDC()` groups main workers by DC and sorts each group by machine address.
- `GetTesters()` returns tester workers sorted by machine address.
- `Worker.HasRoles()` tests whether any role is present.
- `Worker.HasNonWorkerRoles()` excludes the generic `Worker` role.
- `Worker.RolesString()` joins role names with `, `.

## Control Flow

`BuildClusterState()` performs one pass over the supplied events while maintaining an `epochByID` map. It first updates epoch hints from `TLogStart`, `LogRouterStart`, `BackupWorkerStart`, `TLogMetrics`, and `LogRouterMetrics`. Then it processes `Role` events with a non-placeholder machine address.

For each qualifying `Role` event, it extracts transition, role name, and role ID. Missing role names are skipped. A worker is created on first sight of a machine, with address classification from `parseAddress()`. `Transition == "Begin"` appends a role if the same name/ID is not already present, using any epoch currently known for that role ID. `Transition == "End"` removes matching roles. `Refresh` and other transitions do not change state.

After the pass, the function walks all remaining roles and fills any missing epoch from `epochByID`, covering metrics or start events that appeared after the role began.

Grouping and sorting functions iterate the map, filter by `MachineType`, and perform simple in-place O(n^2) address sorting for deterministic UI order.

## State and Persistence Behavior

`BuildClusterState()` returns a fresh state for the given event slice and does not persist across calls. It assumes the input event list represents the desired prefix of trace history. Callers in `ui.go` use it both for full traces and for time-window/prefix display updates.

Worker role slices are mutable and are updated in place while building. Role epoch values are strings copied from trace attributes, so no external storage lifetime issues exist beyond the `TraceEvent` slice itself.

## Dependencies and Integration Points

This file depends on `TraceEvent` from `trace.go`, plus `regexp` and `strings`. It is integrated into the TUI by calls such as `BuildClusterState(m.traceData.Events)` and `BuildClusterState(events)` in `ui.go`, and its grouping helpers support cluster layout/status rendering.

## Risks and Edge Cases

- Regular expressions are compiled on every `parseAddress()` call. For large traces with many machines, package-level precompiled regexes would reduce overhead.
- Sorting is O(n^2); acceptable for small simulation clusters but inefficient if machine counts grow.
- `BuildClusterState()` assumes the event slice is already in chronological order. Passing unsorted events can produce incorrect role lifetimes.
- Role identity is name plus ID. If traces reuse IDs across incompatible role lifetimes or omit IDs, de-duplication/removal may be wrong.
- Unknown transition values are silently ignored.
- Placeholder machine `"0.0.0.0:0"` is skipped, but other invalid placeholders become unknown workers.
- Epoch capture is best-effort and stringly typed; missing or malformed epoch attributes do not produce errors.

## Test Signals

Tests should cover IPv6 and IPv4 address parsing, unknown address formats, role begin/end/refresh sequences, duplicate begin suppression, end without begin, epoch updates from start and metrics events, epoch fill after role creation, grouping by DC, tester extraction, sorted output, and behavior with unsorted input.
