<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-history.go -->
# sources/object-store/minio-mc/cmd/admin-config-history.go

## Purpose
Implements `mc admin config history`, which lists or clears historic configuration changes.

## Important APIs, types, and functions
Defines command flags/help, syntax checker, output message type `configHistoryMessage`, and main handler. Server interaction is through madmin `ListConfigHistoryKV/ClearConfigHistoryKV`.

## Control flow
The handler validates arguments, initializes an admin client from the target alias, branches for help/list/clear modes where applicable, calls the relevant server API, and prints a text or JSON message.

## State and persistence behavior
No local persistence except reading STDIN for import. Commands read or mutate server-side MinIO configuration and may require a service restart, which is reported in output messages.

## Dependencies and integration points
Depends on MinIO CLI globals, madmin config APIs, colorjson/template rendering for output, console coloring, and probe/fatal error handling.

## Risks and test signals
Configuration commands are operationally sensitive: malformed key strings, env-only help, restart-required flags, and history restore ids need strict tests. Signals include API request correctness, JSON output, help rendering, and restart guidance.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-history.go -->
