# sources/sync-backup/restic/internal/backend/b2/config.go

Purpose: Defines B2 backend configuration parsing, bucket-name validation, default options, and environment credential loading.

Important APIs and types: `Config` stores account ID, key, bucket, prefix, and connections. `NewConfig`, `ParseConfig`, `ApplyEnvironment`, and internal `checkBucketName` implement config behavior.

Control flow and state: `ParseConfig` requires `b2:` prefix, splits bucket and optional prefix at `:`, validates bucket names by length and allowed characters, cleans the prefix, and returns defaults with five connections. `ApplyEnvironment` fills account ID and key only when not already set.

Dependencies and integration: Uses `options.Register`, `options.SecretString`, `backend.ApplyEnvironmenter`, regex validation, and path cleaning. The config feeds `Open`, `Create`, and the location registry.

Risks and test signals: Bucket validation is intentionally stricter than generic paths and treats slash-separated strings without a colon as invalid bucket names. `config_test.go` covers valid forms and representative invalid strings.
