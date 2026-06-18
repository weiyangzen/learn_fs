# sources/sync-backup/kopia/repo/maintenance/maintenance_schedule.go

Purpose: stores encrypted maintenance schedule and task history in a repository blob.

Important APIs/types/functions: `RunInfo`, `Schedule`, `ReportRun`, `getAES256GCM`, `TimeToAttemptNextMaintenance`, `GetSchedule`, `SetSchedule`, `buildRunStats`, and constants for blob ID/key purpose.

Control flow: `GetSchedule` reads `kopia.maintenance`, returns an empty schedule if missing, derives an AES-256-GCM key, decrypts nonce-prefixed ciphertext with associated data, and JSON-decodes. `SetSchedule` JSON-encodes, encrypts with a random nonce, and writes the blob. `ReportRun` times a task, stores success/error and serialized stats, caps per-task run history, and persists the schedule.

State/persistence behavior: schedule data is persisted as an encrypted blob separate from manifests. It tracks next quick/full times and recent runs per task.

Dependencies/integration: uses repository key derivation, blob storage, gather buffers, random nonce generation, maintenance stats serialization, and ownership params.

Risks/test signals: corrupt or short blobs fail to load; losing schedule write errors during `ReportRun` is logged but the task error is returned. Tests cover schedule persistence, next-attempt calculation, and stats round trips.
