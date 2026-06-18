<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_windows.go -->
# sources/sync-backup/restic/internal/restorer/truncate_windows.go

## Purpose
Provides Windows-specific sparse truncation support.

## Important APIs and Control Flow
`truncateSparse` marks the file sparse using Windows control codes before setting the file size. Control flow performs the Windows sparse-file setup, then truncates to the requested logical size.

## State, Persistence, Dependencies, and Integration
Persistent state is the Windows sparse-file attribute and file size. It depends on Windows syscalls and integrates with `fileswriter.go`.

## Risks and Test Signals
Risks are syscall failures on unsupported filesystems or handles; Windows restore tests and cross-platform sparse tests are the relevant signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/truncate_windows.go -->
