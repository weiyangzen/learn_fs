# sources/object-store/minio/cmd/typed-errors.go

Purpose: centralizes package-level sentinel errors for common MinIO command-layer failure conditions. These errors are used for identity, IAM, S3 API, multipart upload, range, decompression, RPC, and SFTP validation paths.

Important APIs and values: exported names are package-private `var` sentinels such as `errInvalidArgument`, `errMethodNotAllowed`, `errSignatureMismatch`, `errDataTooLarge`, `errServerNotInitialized`, `errInvalidRange`, `errNoSuchUser`, `errNoSuchServiceAccount`, `errNoSuchPolicy`, `errIAMNotInitialized`, `errUploadIDNotFound`, `errSessionPolicyTooLarge`, `errSftpPublicKeyWithoutCert`, and `errGroupNameContainsReservedChars`.

Control flow: there are no functions. Callers compare, wrap, or convert these sentinel errors through API/admin error conversion code. Keeping them as `errors.New` variables enables identity comparisons with `errors.Is` when wrapped.

State and persistence: immutable process-level sentinel values. No runtime state or persistence.

Dependencies and integration points: depends only on Go `errors`. Integrates broadly with object API handlers, IAM subsystem, admin APIs, STS/session policy validation, multipart upload handling, decompression checks, and SFTP authentication.

Risks: changing message text can alter client-facing diagnostics or tests if conversion code exposes the error string. Replacing sentinel variables with new instances in other files would break identity comparisons. Some comments reveal specific behavior expectations, such as LDAP warning text and session policy max size.

Test signals: no local tests. Coverage is indirect through handlers and subsystem tests that expect these errors to map to specific API/admin responses.
