# sources/object-store/minio-mc/cmd/admin-logs.go

## Purpose
Implements `mc admin logs`, streaming MinIO server log entries, optionally filtered by node, last count, and log type.

## Important APIs, types, and functions
Key symbols include `logsShowFlags`, `adminLogsCmd`, `checkLogsShowSyntax`, `logMessage`, `getLogTime`, and `mainAdminLogs`. It calls `AdminClient.GetLogs`.

## Control flow
The handler validates arguments, configures colors, parses target and optional node, validates `--last` and `--type`, creates an admin client, opens a cancelable context, then ranges over the log channel. Each successful record with a deployment ID is printed; node names are suppressed when a specific node was requested.

## State and persistence behavior
This command is read-only and streaming. It holds transient context state and reads server logs; it does not persist log data locally.

## Dependencies and integration points
It integrates `madmin.LogInfo`, shared HTTP/admin client setup, global output mode, colorized node names, API/trace formatting, and `probe` fatal handling for stream errors.

## Risks and edge cases
`checkLogsShowSyntax` allows up to three args although usage documents target plus optional node. A `last` flag is only validated when explicitly set, leaving value zero for unlimited/default server behavior. Logs without deployment IDs are dropped.

## Test signals
Tests should cover type validation, positive `--last` validation, node-name suppression, time parsing fallback, trace variable/source formatting, JSON output, stream error handling, and context cancellation behavior.
