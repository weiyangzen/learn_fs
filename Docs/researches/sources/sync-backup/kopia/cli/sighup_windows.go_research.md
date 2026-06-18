<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_windows.go -->
# sources/sync-backup/kopia/cli/sighup_windows.go

## Purpose
Provides the Windows stub for external configuration reload requests.

## Important APIs, Types, And Functions
Defines `onExternalConfigReloadRequest` as a no-op because SIGHUP is not supported on Windows.

## Control Flow
Control flow intentionally ignores the callback. Server refresh must be triggered by other mechanisms on Windows.

## State And Persistence Behavior
No state or persistence behavior exists.

## Dependencies And Integration Points
Depends on Windows build-tag selection by filename.

## Risks And Edge Cases
Platform behavior differs from Unix; code relying on SIGHUP refresh must not assume it works on Windows.

## Test Signals
Build coverage on Windows and server refresh tests through explicit commands are the relevant signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/sighup_windows.go -->
