# sources/sync-backup/restic/internal/backend/azure/config_test.go

Purpose: Parse tests for Azure backend locations.

Important APIs and functions: `configTests` defines expected `Config` values and `TestParseConfig` delegates to `backend/test.ParseConfigTester`.

Control flow and state: The tests cover root prefix, nested prefix, and trailing slash cleanup for strings of the form `azure:container-name:/...`.

Dependencies and integration: Uses the backend test helper package and `ParseConfig` from `config.go`.

Risks and test signals: Provides basic positive parse coverage. It does not cover invalid Azure config strings or environment application.
