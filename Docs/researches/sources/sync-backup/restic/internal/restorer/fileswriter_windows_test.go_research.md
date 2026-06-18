<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go

## Purpose
Provides the Windows expected error helper for `fileswriter_test.go`.

## Important APIs and Control Flow
`notEmptyDirError` returns `syscall.ERROR_DIR_NOT_EMPTY` for Windows directory replacement assertions. No control flow beyond returning the platform error constant.

## State, Persistence, Dependencies, and Integration
No state is stored. The file is selected only on Windows by filename/build constraints.

## Risks and Test Signals
Its test signal is indirect but necessary for portable filled-directory overwrite tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_windows_test.go -->
