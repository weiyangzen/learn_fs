<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_rclone.go -->
# sources/sync-backup/kopia/cli/storage_rclone.go

## Purpose
Implements rclone-based provider flags for extra-provider builds; the provider is marked not maintained.

## Important APIs, Types, And Functions
Defines `storageRcloneFlags`, `Setup`, `Connect`, and registration. Flags include remote path, flat layout, executable, args/env, embedded config, debug, transfer close behavior, list parallelism, atomic writes, startup timeout, and throttling.

## Control Flow
Connect sets directory sharding, optionally reads and embeds an rclone config file, then calls `rclone.New`.

## State And Persistence Behavior
Persistent repository config can include embedded rclone config text and backend options. Actual storage is mediated by an external rclone process.

## Dependencies And Integration Points
Integrates rclone blob backend, storage registry, file reading, sharding helper, and throttling.

## Risks And Edge Cases
External process startup, embedded config secrecy, atomic-write assumptions, and not-maintained status are primary risks. Args/env are passed through with limited validation.

## Test Signals
Tests should cover embedded config read failures, flat sharding, option propagation, and startup timeout parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/storage_rclone.go -->
