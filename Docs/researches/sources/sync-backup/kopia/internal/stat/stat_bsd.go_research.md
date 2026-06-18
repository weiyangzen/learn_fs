<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_bsd.go -->
# sources/sync-backup/kopia/internal/stat/stat_bsd.go

- Purpose: Provides OpenBSD-specific filesystem allocation and block-size helpers.
- Important APIs/types/functions: `diskBlockSize`, `errInvalidBlockSize`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: `GetFileAllocSize` calls `syscall.Stat` and multiplies block count by 512. `GetBlockSize` calls `syscall.Statfs`, validates `F_bsize`, and returns it.
- State and persistence: Reads filesystem metadata only; no mutation or repository state.
- Dependencies and integration points: Build-constrained to `openbsd`; depends on `syscall` and `pkg/errors`.
- Risks and edge cases: Platform syscall fields differ from other Unix variants, requiring this separate file.
- Test signals: `stat_test.go` runs on non-Windows platforms and covers positive block/allocation sizes.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_bsd.go -->
