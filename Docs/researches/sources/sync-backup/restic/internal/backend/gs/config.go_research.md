# sources/sync-backup/restic/internal/backend/gs/config.go

Purpose: Defines Google Cloud Storage backend configuration parsing and environment application.

Important APIs and types: `Config` stores project ID, bucket, prefix, connection count, and creation region. `NewConfig`, `ParseConfig`, and `ApplyEnvironment` implement defaults, location parsing, and environment fill-in.

Control flow and state: `ParseConfig` requires `gs:` and a bucket/path colon, cleans the prefix, and defaults to five connections in region `us`. `ApplyEnvironment` fills `ProjectID` from `GOOGLE_PROJECT_ID` when unset.

Dependencies and integration: Uses `options.Register`, `backend.ApplyEnvironmenter`, path cleaning, and errors. The config feeds `gs.Open` and `gs.Create`.

Risks and test signals: Risks include missing project ID during bucket creation and minimal validation of bucket names. `config_test.go` covers valid parse forms.
