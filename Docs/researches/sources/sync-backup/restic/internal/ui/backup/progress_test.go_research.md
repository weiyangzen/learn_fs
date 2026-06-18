<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress_test.go -->
# sources/sync-backup/restic/internal/ui/backup/progress_test.go

## Purpose
Tests backup progress state transitions with a mock printer.

## Important APIs and Control Flow
`mockPrinter` records selected messages and final snapshot ID. `TestProgress` starts a file, completes blobs/items, reports totals, handles errors, and finishes to verify expected printer calls and state updates. Control flow uses a short update interval and explicit method calls rather than running a full backup.

## State, Persistence, Dependencies, and Integration
State is mock-printer fields protected by a mutex plus progress counters. Dependencies include archiver/data node types and noop progress printer.

## Risks and Test Signals
The test catches callback mapping and finish regressions but does not deeply test periodic timing or JSON/text output.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/ui/backup/progress_test.go -->
