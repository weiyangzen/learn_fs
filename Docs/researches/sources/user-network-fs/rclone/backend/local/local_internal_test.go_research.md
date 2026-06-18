
# sources/user-network-fs/rclone/backend/local/local_internal_test.go

## Purpose
Provides local backend unit and integration-style tests for update detection, symlinks, hashing, metadata, filters, and copy behavior.

## Important APIs, Types, And Control Flow
`TestMain` initializes fstest. `TestUpdatingCheck` verifies `localOpenFile.Read` fails when source size/mtime changes unless `NoCheckUpdated` is set. Symlink tests switch between no flags, `--copy-links`, and `--links`, check `.rclonelink` translation, NewFs root-file rules, range reads, and conflict errors. Hash tests validate `hash.None`, hash recomputation after update, and cache clearing after remove. Metadata tests exercise file and symlink metadata/xattrs and confirm symlink metadata does not alter the target. Filter tests validate filter-aware listing and symlink filtering. Copy tests ensure translated symlinks recreate links and copy-links produces regular files.

## State And Persistence
Creates temporary local trees with files, directories, symlinks, xattrs, modes, and timestamps. Cleanup is handled by fstest runs and defers.

## Dependencies And Integration Points
Uses rclone `filter`, `accounting`, `operations`, `object`, `hash`, `readers`, `file`, and testify. It tests both direct local helpers and rclone operation-level copy behavior.

## Risks And Test Signals
This is the primary local backend regression suite. It explicitly covers security-sensitive symlink metadata isolation and behavior that differs by OS capability flags such as xattrs, link time setting, and birth time setting.
