# sources/sync-backup/kopia/repo/blob/gcs/gcs_options.go

Purpose: defines persistent options for Google Cloud Storage-backed repositories.

Important APIs/types/functions: `Options` with bucket name, prefix, service account credentials file or raw JSON, read-only flag, throttling limits, and optional point-in-time timestamp.

Control flow: no functions are implemented in this file. `gcs_storage.go` performs validation/client creation and `gcs_pit.go` handles `PointInTime`.

State and persistence behavior: this struct is serialized in repository connection config. Raw credential JSON is marked sensitive; read-only changes OAuth scope during client creation.

Dependencies/integration points: consumed by GCS provider creation, throttling wrappers, PIT wrapper, and config serialization. Risks include backward-compatible JSON field pressure, mutually exclusive credential sources resolved elsewhere, and read-only scope preventing mutations only at the provider credential level. Tests cover normal/invalid storage, credentials from environment, cleanup, immutability, and versioned PIT.
