<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout.go -->
# sources/sync-backup/restic/internal/backend/layout/layout.go

## Purpose
Defines the storage layout abstraction used by backends to map restic handles to concrete file/object paths.

## Important APIs, Types, And Functions
Layout interface exposes Filename, Dirname, Basedir, Paths, and Name.

## Control Flow
No control flow beyond interface definition; implementations supply path mapping for local/SFTP/S3/Swift and REST.

## State And Persistence Behavior
No state or persistence in this file; implementations encode layout state such as repository prefix or base URL.

## Dependencies And Integration Points
Depends on internal/backend for Handle and FileType types.

## Risks And Edge Cases
Any layout implementation must keep Filename, Dirname, and Basedir consistent or listing/deletion will miss objects.

## Test Signals
Exercised by layout tests and by backend suite tests that create, list, and remove files.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout.go -->
