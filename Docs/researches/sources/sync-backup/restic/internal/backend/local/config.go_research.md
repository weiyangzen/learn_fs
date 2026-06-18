<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config.go -->
# sources/sync-backup/restic/internal/backend/local/config.go

## Purpose
Parses and registers configuration for local filesystem repositories.

## Important APIs, Types, And Functions
Config, NewConfig, init option registration, and ParseConfig are the API.

## Control Flow
ParseConfig requires the local: prefix, strips it, and leaves the remaining path unchanged so platform-specific paths and colons are preserved.

## State And Persistence Behavior
Config stores Path and Connections only; no persistence happens here.

## Dependencies And Integration Points
Depends on strings, internal/errors, and internal/options. Used by location factory and local.Open/Create.

## Risks And Edge Cases
Invalid prefix is rejected; path normalization is intentionally not done, which preserves Windows paths but leaves validation to filesystem operations.

## Test Signals
config_test.go covers absolute, relative, colon-containing, and Windows-style paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config.go -->
