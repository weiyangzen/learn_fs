<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag.go -->
# sources/object-store/minio-mc/cmd/support-diag.go

Purpose: implements `mc support diag` / `diagnostics`, collecting MinIO health data, optionally saving it for airgapped use, and otherwise uploading it to SUBNET.

Important APIs/types/functions: `supportDiagCmd`, `supportDiagFlags`, `supportDiagMessage`, `checkSupportDiagSyntax`, `execSupportDiag`, `fetchServerDiagInfo`, `TarGZHealthInfo`, `tarGZ`, `HealthDataTypeSlice`, and `HealthDataTypeFlag` define CLI behavior, serialization, server collection, and custom flag parsing. Constants define anonymization modes.

Control flow: `mainSupportDiag` validates one target and anonymization mode, initializes SUBNET connectivity, enforces registration when needed, builds an admin client, and calls `execSupportDiag`. Non-airgapped mode pre-fetches upload URL/headers before collection. `fetchServerDiagInfo` resolves requested health sections, starts progress spinners for non-JSON output, calls `ServerHealthInfo`, then decodes version-specific streaming health formats. Version 0 is mapped to V1 after fetching `ServerInfo`; version 2 decodes `HealthInfoV2`; current version delegates to `receiveHealthInfo`. Results are gzip-compressed as JSON header plus health payload, saved locally, and uploaded unless airgapped.

State and persistence: writes a `<alias>-health_<timestamp>.json.gz` report locally. In non-airgapped mode, `SubnetFileUploader` deletes the file after successful upload. It does not mutate server config.

Dependencies and integration points: integrates with MinIO admin health APIs, SUBNET upload helpers, support registration, global JSON/airgap flags, colorized console output, and `madmin.HealthDataTypesMap/List`.

Risks and test signals: streaming decode and spinner cancellation are sensitive to partial responses and deadlines. Tests should cover invalid anonymization, custom health type parsing, airgapped JSON behavior, upload failure, gzip contents, and old health-version conversion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/support-diag.go -->
