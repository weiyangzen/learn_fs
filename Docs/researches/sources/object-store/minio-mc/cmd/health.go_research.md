# sources/object-store/minio-mc/cmd/health.go

Purpose: Defines common interfaces and header structs for subnet health report output.

Important APIs/types/functions: `HealthReportInfo`, `HealthReportHeader`, `Health`, and `SchemaVersion`.

Control flow: No executable logic. The interface requires timestamp/status/error accessors plus the shared `message` interface for printable output.

State and persistence: Data structures only.

Dependencies/integration: Used by versioned health report implementations such as `ClusterHealthV1`.

Risks: Minimal; schema stability matters for consumers expecting `{"subnet":{"health":{"version":"v1"}}}` style headers.

Test signals: No direct tests.
