# sources/object-store/minio/cmd/sts-errors.go

Purpose: maps internal STS error codes to AWS-style XML error responses and HTTP status codes.

Important APIs/types/functions: `writeSTSErrorResponse` builds and writes an `STSErrorResponse`. `STSError` describes code, description, and HTTP status. `STSErrorCode` enumerates access denied, missing/invalid parameters, expired tokens, malformed policies, TLS certificate errors, STS/IAM initialization errors, upstream failures, and internal errors. `stsErrorCodeMap.ToSTSErr` provides fallback to internal error. `stsErrCodes` contains the concrete AWS-style code strings and statuses.

Control flow: handlers pass an `STSErrorCode` plus optional concrete error. `writeSTSErrorResponse` uses the mapped description unless a concrete error is supplied, attaches the current request ID, logs internal/upstream failures, XML-encodes the response, and writes it with the mapped status.

State and persistence behavior: no persistent state. Error mappings are part of the public STS API behavior and audit/debug surface.

Dependencies/integration: integrates with MinIO HTTP response helpers, request ID headers, XML encoding, and STS handler branches. `apiToSTSError` in `sts-handlers.go` maps S3 auth errors into these codes.

Risks/test signals: returning raw `err.Error()` improves diagnostics but can expose upstream messages, especially for identity providers. Missing map entries default to internal error. There are broad STS integration tests elsewhere, but no focused table test here for every mapping/status.
