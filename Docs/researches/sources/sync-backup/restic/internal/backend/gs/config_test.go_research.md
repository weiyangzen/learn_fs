# sources/sync-backup/restic/internal/backend/gs/config_test.go

Purpose: Parse tests for Google Cloud Storage backend locations.

Important APIs and functions: `configTests` defines expected configs for root, nested, and trailing-slash prefixes. `TestParseConfig` delegates to `backend/test.ParseConfigTester`.

Control flow and state: The tests verify default connections and region along with parsed bucket/prefix fields.

Dependencies and integration: Uses package-local `ParseConfig` and backend test utilities.

Risks and test signals: Provides positive parser coverage but not invalid strings or environment application.
