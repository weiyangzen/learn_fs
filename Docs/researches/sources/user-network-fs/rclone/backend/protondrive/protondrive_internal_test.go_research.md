# sources/user-network-fs/rclone/backend/protondrive/protondrive_internal_test.go

## Purpose
Proton Drive internal unit tests: validates app-version derivation and retry classification without live credentials.

## Important APIs, Types, And Functions
Important surface: protonDriveAppVersionPattern, TestProtonDriveAppVersionFromRcloneVersion, TestShouldRetry.

## Control Flow
table tests call helper functions with releases, dev/beta builds, invalid versions, API errors, wrapped errors, and canceled contexts

## State And Persistence
in-memory only.

## Dependencies And Integration Points
go-proton-api APIError and testify assert.

## Risks And Test Signals
Risks and useful test signals: covers main intended cases; gaps include alpha/RC and SDK retry-after integration.
