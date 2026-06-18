<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config.go -->
# sources/sync-backup/restic/internal/backend/rclone/config.go

## Purpose
Parses and registers rclone backend configuration.

## Important APIs, Types, And Functions
Config, defaultConfig, NewConfig, init, and ParseConfig are the API.

## Control Flow
ParseConfig requires rclone:, strips the prefix, and stores the remaining remote while applying defaults for program, args, connections, and timeout.

## State And Persistence Behavior
No persistence; config controls later subprocess creation.

## Dependencies And Integration Points
Depends on strings, time, internal/errors/options.

## Risks And Edge Cases
Remote strings are not validated here; command/args splitting happens in backend.go and can fail later.

## Test Signals
config_test.go covers the canonical remote parse case.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config.go -->
