<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_windows.go -->
# sources/sync-backup/kopia/internal/stat/stat_windows.go

- Purpose: Provides Windows stubs for stat helpers where sparse allocation/block-size behavior is not implemented.
- Important APIs/types/functions: `errNotImplemented`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: Both public functions immediately return zero and `errNotImplemented`.
- State and persistence: No state or filesystem mutation.
- Dependencies and integration points: Build-constrained to `windows`; callers must handle unsupported behavior.
- Risks and edge cases: Any cross-platform caller expecting real values must avoid or special-case Windows.
- Test signals: `stat_test.go` is excluded on Windows, so this stub is not directly tested here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_windows.go -->
