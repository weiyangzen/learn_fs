<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows_test.go -->
# sources/sync-backup/restic/internal/restorer/restorer_windows_test.go

## Purpose
Exercises Windows-specific restore behavior for file attributes, directory attributes, overwrites, encrypted files, named streams, and delete case-insensitivity.

## Important APIs and Control Flow
The file defines `FileAttributes`, `NodeInfo`, data-stream helpers, Windows attribute conversion, encrypted-file creation, and verification helpers. Tests generate combinations of readonly/hidden/system/archive/encrypted attributes for files and directories, both fresh and overwritten, then verify restored attributes and content. Control flow builds snapshots with generic Windows attributes, optionally pre-creates destination items with different attributes, restores, and checks Win32 attribute bits via syscall/windows APIs.

## State, Persistence, Dependencies, and Integration
State is Windows filesystem metadata, temporary directories, and synthetic repository snapshots. Dependencies include `data.WindowsAttrsToGenericAttributes`, `golang.org/x/sys/windows`, and restorer snapshot helpers.

## Risks and Test Signals
The suite gives broad Windows metadata coverage. Risks remain around platform privileges, encrypted filesystem support, and combinatorial runtime cost.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/restorer_windows_test.go -->
