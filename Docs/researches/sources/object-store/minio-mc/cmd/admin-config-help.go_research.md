<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-help.go -->
# sources/object-store/minio-mc/cmd/admin-config-help.go

## Purpose
Shared rendering helpers for MinIO admin config help output in text and JSON forms.

## Important APIs, types, and functions
Defines `HelpTmpl`, `funcMap`, parsed `HelpTemplate` and `HelpEnvTemplate`, and `configHelpMessage` with `String` and `JSON`.

## Control flow
Commands construct `configHelpMessage` from madmin help responses. `String` chooses normal or env-only template and executes it into a buffer; `JSON` marshals the raw help response.

## State and persistence behavior
No state. It formats server-provided config help metadata.

## Dependencies and integration points
Used by config get/set/reset paths. Depends on Go templates, color functions, colorjson, console/probe helpers, and madmin help response shape.

## Risks and test signals
Template field drift in madmin help structs can break output at runtime. Tests should cover env-only and normal templates, JSON output, and empty subsystem help.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/admin-config-help.go -->
