# sources/object-store/minio-mc/cmd/encrypt-info.go

Purpose: Implements `mc encrypt info` to display bucket auto-encryption status.

Important APIs/types/functions: `encryptInfoCmd`, `checkEncryptInfoSyntax`, `encryptInfoMessage`, and `mainEncryptInfo`.

Control flow: Requires one target, creates a client, calls `GetEncryption`, maps algorithm/key ID into output, and prints human or JSON output. String output distinguishes disabled, SSE-S3, and SSE-KMS with key ID.

State and persistence: Read-only against remote bucket encryption config.

Dependencies/integration: Uses client encryption API, global context, console/color, and colorjson.

Risks: String output assumes non-empty algorithm without key ID means SSE-S3, so future algorithms could be misreported.

Test signals: No direct tests.
