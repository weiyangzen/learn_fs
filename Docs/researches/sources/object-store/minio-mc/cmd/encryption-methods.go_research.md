# sources/object-store/minio-mc/cmd/encryption-methods.go

Purpose: Parses and validates command-line server-side encryption options for object operations.

Important APIs/types/functions: `sseKeyType`, `prefixSSEPair`, `byPrefixLength`, `getSSE`, `validateAndCreateEncryptionKeys`, `validateAndParseKey`, `validateOverLappingSSEKeys`, `splitKey`, `parseSSEKey`, and `validKMSKeyName`.

Control flow: CLI string slices are parsed for KMS, S3, and SSE-C. Each key is split at the last `=`, validated, converted to a minio-go `encrypt.ServerSide`, checked for matching command args and configured aliases, checked for overlapping prefixes, then sorted by longest prefix for lookup.

State and persistence: Builds per-command in-memory maps from alias to prefix/SSE pairs. No persistence.

Dependencies/integration: Uses `mustGetHostConfig`, minio-go encryption constructors, global CLI args, and SSE-specific error helpers.

Risks: Alias existence is checked via config/env and can be nil if config is unavailable. Prefix matching uses simple `strings.HasPrefix`, so ambiguous path boundaries must be controlled by overlap validation. KMS key-name validation is intentionally restrictive.

Test signals: `encryption-methods_test.go` exercises parsing for SSE-C base64/hex, unusual prefixes, invalid keys, KMS names, and SSE-S3.
