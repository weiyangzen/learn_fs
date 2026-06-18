# sources/object-store/minio-mc/cmd/admin-scanner-trace.go

## Purpose
Implements `mc admin scanner trace`, streaming MinIO service trace events filtered to scanner operations.

## Important APIs, types, and functions
`adminScannerTraceFlags` defines verbose, function, node, path, size, request/response, and duration filters. `adminScannerTraceCmd`, `checkAdminScannerTraceSyntax`, and `mainAdminScannerTrace` drive the command.

## Control flow
The handler requires one target and enforces that size filters include `--filter-size`. It initializes trace colors, creates an admin client, builds tracing options scoped to `scanner`, builds matching options from CLI flags, then ranges over `ServiceTrace` events and prints only those matching the filters.

## State and persistence behavior
The command is streaming and read-only. It holds a cancelable context but persists no trace data.

## Dependencies and integration points
It integrates shared tracing helpers (`tracingOpts`, `matchingOpts`, `printTrace`), MinIO admin service trace API, global context, and console node/color themes.

## Risks and edge cases
Some examples reference request-header filtering that is not declared in this file, implying shared flags or stale help text. Long-running streams depend on user cancellation. Filter-size parsing is delegated to shared tracing helpers.

## Test signals
Tests should cover syntax, missing filter-size rejection, tracing option scope of `scanner`, matching filter behavior, verbose versus normal trace output, stream errors, and cancellation.
