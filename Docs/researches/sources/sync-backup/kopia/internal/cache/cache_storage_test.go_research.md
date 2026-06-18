## sources/sync-backup/kopia/internal/cache/cache_storage_test.go

Purpose: tests cache storage creation edge cases.

Important APIs/types/functions: `TestNewStorageOrNil`.

Control flow, state, and persistence: calls `NewStorageOrNil` with disabled cache settings, a relative path, and an injected `mkdirAll` failure. It restores the package variable after the test.

Dependencies and integration points: uses temporary directories and test logging.

Risks and test signals: covers the main guardrails around cache directory setup. Does not validate successful filesystem storage behavior beyond construction in other content cache tests.
