# sources/sync-backup/kopia/internal/ospath/ospath_windows_test.go

Purpose: Windows-only tests for `SafeLongFilename`.

Important APIs/types/functions: `TestSafeLongFilename_Windows`.

Control flow: table cases feed normal drive paths, UNC paths, relative paths, and existing extended paths into the helper and compare exact strings.

State and persistence behavior: no external state.

Dependencies and integration points: validates path strings used by Windows file operations elsewhere in Kopia.

Risks and test signals: these tests are build-tagged for Windows and will not run on Unix CI; cross-platform coverage depends on Windows jobs.
