<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_default.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_default.go

## Purpose
Implements the default on-disk/object layout: config at repository root, pack files under data/xx/name, and metadata under snapshots, index, locks, and keys.

## Important APIs, Types, And Functions
DefaultLayout, NewDefaultLayout, String, Name, Dirname, Filename, Paths, and Basedir form the API.

## Control Flow
Dirname selects the file-type base path and adds the first two pack-name characters as a data subdirectory; Filename special-cases config; Paths enumerates base dirs plus all 256 data subdirs.

## State And Persistence Behavior
Stores only layout configuration: base path and join function. Persistence is external through backends that use returned paths.

## Dependencies And Integration Points
Depends on encoding/hex and internal/backend. Consumers include local, sftp, s3, swift, and layout tests.

## Risks And Edge Cases
Short pack names bypass subdir insertion; callers must provide valid handles. Map iteration order in Paths is not stable, so tests sort before comparing.

## Test Signals
Covered by layout/layout_test.go plus backend fixture layout tests for local and sftp.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_default.go -->
