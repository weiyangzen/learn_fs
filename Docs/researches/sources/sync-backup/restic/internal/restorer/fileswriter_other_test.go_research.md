<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go -->
# sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go

## Purpose
Provides the non-Windows expected error helper for `fileswriter_test.go`.

## Important APIs and Control Flow
`notEmptyDirError` returns `syscall.ENOTEMPTY` so recursive overwrite tests can compare portable error values. There is no runtime flow beyond returning the platform constant.

## State, Persistence, Dependencies, and Integration
No state is stored; the file is selected on non-Windows platforms by build tag.

## Risks and Test Signals
The test signal is indirect: it keeps filled-directory overwrite assertions accurate on Unix-like platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/restorer/fileswriter_other_test.go -->
