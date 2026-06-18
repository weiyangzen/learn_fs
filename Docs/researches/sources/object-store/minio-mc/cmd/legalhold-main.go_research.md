# Research: sources/object-store/minio-mc/cmd/legalhold-main.go

Purpose: registers legalhold commands and provides shared object-lock status helpers and success message type.

Important APIs/types/functions: `legalHoldSubcommands`, `legalHoldCmd`, `legalHoldCmdMessage`, `isBucketLockEnabled`, `getBucketLockStatus`, and `mainLegalHold`.

Control flow: command dispatches set, clear, and info. `getBucketLockStatus` creates a client, strips object path to bucket root for S3 clients, calls `GetObjectLockConfig`, and maps not-configured/not-implemented responses to sentinel errors. `isBucketLockEnabled` converts those sentinel errors to false.

State and persistence: read-only bucket object-lock config lookup; message type is output-only.

Dependencies/integration points: S3 client implementation, MinIO error response conversion, HTTP status codes, shared console output.

Risks: non-S3 targets are treated as object-lock unsupported. Object path stripping assumes URL/object mapping from `S3Client.url2BucketAndObject`.

Test signals: no direct tests; should cover no object-lock config, unsupported filesystem target, S3 bucket URL versus object URL, and enabled status.
