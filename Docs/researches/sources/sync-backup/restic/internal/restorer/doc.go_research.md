<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/doc.go -->
# sources/sync-backup/restic/internal/restorer/doc.go

## Purpose
Documents the restorer package and explains the high-level restore architecture.

## Important APIs and Control Flow
The package comment describes the two-pass restore approach: create directories and collect file content first, then restore metadata, hardlinks, and special nodes after file data exists. It has no executable control flow; it is important because it frames how `restorer.go`, `filerestorer.go`, and `fileswriter.go` cooperate.

## State, Persistence, Dependencies, and Integration
No state or dependencies beyond the package declaration. Integration is documentation for callers and maintainers of restore behavior.

## Risks and Test Signals
Risk is documentation drift as restore behavior changes. Tests in the restorer package provide the actual behavioral signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/doc.go -->
