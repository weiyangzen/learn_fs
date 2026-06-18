# sources/sync-backup/restic/internal/fs/stat_darwin.go

Purpose: macOS stat conversion plus dataless-file detection.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts POSIX stat fields and stores the raw `*syscall.Stat_t` in `sys`. `RecallOnDataAccess` checks `unix.SF_DATALESS` to detect cloud-only placeholder files.

Dependencies and integration: Used by backup code to avoid unintended cloud downloads when checking recall-on-data-access status.

Risks: `RecallOnDataAccess` errors if `sys` is missing or not a Darwin stat struct. HFS+ timestamp precision differences are handled in tests.

Test signals: `stat_darwin_test.go` covers real regular files, mocked dataless files, regular mocks, and missing sys errors.
