# sources/sync-backup/kopia/repo/token.go

Purpose: encodes and decodes opaque repository connection tokens containing storage connection info and optional password.

Important APIs/types/functions: `tokenInfo` JSON schema has `Version`, `Storage`, and optional `Password`. `directRepository.Token` delegates to `EncodeToken`. `EncodeToken` marshals version `1` and raw-URL-base64 encodes it. `DecodeToken` decodes, unmarshals, checks version, and returns `blob.ConnectionInfo` plus password.

Control flow: decoding intentionally returns generic `"unable to decode token"` for base64 and JSON failures, and `"unsupported token version"` for version mismatch.

State and persistence behavior: tokens are serialized connection state and may persist passwords if provided. No repository mutation occurs.

Dependencies/integration: depends on `blob.ConnectionInfo` JSON and standard base64/JSON. Used for sharing or reconnecting to repositories.

Risks: tokens can contain plaintext passwords inside base64 JSON, so callers must treat them as secrets. Schema versioning is strict; future versions need migration or compatibility handling.

Test signals: no direct tests in this subset; token behavior may be covered elsewhere.
