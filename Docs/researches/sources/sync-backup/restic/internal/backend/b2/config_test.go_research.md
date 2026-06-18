# sources/sync-backup/restic/internal/backend/b2/config_test.go

Purpose: Parse and validation tests for B2 backend locations.

Important APIs and functions: `configTests` covers valid strings; `invalidConfigTests` covers missing prefix, missing bucket, underscores, and slash-without-colon mistakes. `TestParseConfig` and `TestInvalidConfig` exercise `ParseConfig`.

Control flow and state: Positive tests use `backend/test.ParseConfigTester`. Negative tests assert exact error strings and that invalid configs do not return nil errors.

Dependencies and integration: Uses `internal/backend/test` and package-local parsing.

Risks and test signals: These tests guard the user-facing location grammar and bucket-name constraints. They do not cover environment variable application.
