<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-console.go -->
# sources/object-store/minio-mc/cmd/admin-console.go

## Purpose
Deprecated compatibility wrapper for `mc admin console`, redirecting users to `mc admin logs` while preserving old flags.

## Important APIs, types, and functions
Defines flags `--limit/-l` and `--type/-t`, hidden `adminConsoleCmd`, and `mainAdminConsole`.

## Control flow
The handler builds a replacement command string starting with `mc admin logs`, maps `limit` to `--last`, lowercases `type`, appends positional args, and calls `deprecatedError`.

## State and persistence behavior
No state and no server calls.

## Dependencies and integration points
Depends on MinIO CLI flag parsing and shared deprecation messaging.

## Risks and test signals
Replacement command synthesis must match the current logs command flags. Tests should cover no flags, limit, type case normalization, and passthrough args.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-console.go -->
