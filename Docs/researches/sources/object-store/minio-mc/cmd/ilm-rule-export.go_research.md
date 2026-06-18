# Research: sources/object-store/minio-mc/cmd/ilm-rule-export.go

Purpose: implements `mc ilm rule export`, printing bucket lifecycle configuration as JSON.

Important APIs/types/functions: `ilmExportCmd`, `ilmExportMessage`, `checkILMExportSyntax`, and `mainILMExport`.

Control flow: validates one target, creates a client, fetches lifecycle config and updated timestamp, errors when no rules exist, and prints either raw config in console mode or wrapped status/target/config JSON in JSON mode.

State and persistence: read-only server operation.

Dependencies/integration points: MinIO client `GetLifecycle`, colorjson, lifecycle configuration types.

Risks: console and JSON outputs have different envelopes. Empty lifecycle configuration is treated as an error rather than exporting an empty config.

Test signals: no direct tests; should cover empty config, JSON envelope, and updatedAt propagation.
