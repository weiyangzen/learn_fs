# sources/object-store/minio-mc/cmd/admin-decom-status.go

## Purpose
Implements `mc admin decommission status`, the human and JSON status view for MinIO server-pool decommissioning. It can show one pool passed as a second argument or list the decommission state of every pool.

## Important APIs, types, and functions
The command is `adminDecommissionStatusCmd`; `checkAdminDecommissionStatusSyntax` permits one or two arguments. `mainAdminDecommissionStatus` uses `newAdminClient`, `StatusPool`, `ListPoolsStatus`, `json.MarshalIndent`, `console.NewTable`, and `humanize.IBytes/RelTime/Ordinal`.

## Control flow
The handler cleans the target alias, creates an admin client, then branches on an optional pool argument. A single-pool request fetches `StatusPool`, emits JSON directly when requested, otherwise derives a completion, failed, canceled, active-rate, starting, or unscheduled message. A list request fetches all pools and renders a table of pool id, command line, usage, and status.

## State and persistence behavior
The file does not persist local state. It observes server-side decommission metadata, especially `StartTime`, sizes, and terminal booleans, and converts those into display state. Its rate calculation is transient and based on current wall-clock time.

## Dependencies and integration points
It integrates the `cli` command tree, `madmin-go` admin pool APIs through the shared client, global JSON handling, MinIO console tables, and color helpers from the surrounding `cmd` package.

## Risks and edge cases
Total size can be zero, so list output has an explicit zero-capacity branch. Single-pool speed only appears when the used-size delta and elapsed duration are meaningful; otherwise it says startup. The failed/canceled messages are colored as success text, which may be confusing.

## Test signals
Useful tests should cover one-argument list mode, two-argument pool mode, JSON marshal output, zero-size pools, each terminal decommission flag, active rate calculation after ten seconds, and syntax rejection for zero or more than two arguments.
