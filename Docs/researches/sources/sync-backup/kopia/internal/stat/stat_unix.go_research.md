<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_unix.go -->
# sources/sync-backup/kopia/internal/stat/stat_unix.go

- Purpose: Provides Linux, FreeBSD, and Darwin filesystem allocation and block-size helpers.
- Important APIs/types/functions: `diskBlockSize`, `errInvalidBlockSize`, `GetFileAllocSize`, `GetBlockSize`.
- Control flow: `GetFileAllocSize` reads `syscall.Stat_t.Blocks` and multiplies by 512; `GetBlockSize` validates `syscall.Statfs_t.Bsize`.
- State and persistence: Reads filesystem metadata only.
- Dependencies and integration points: Build-constrained to `linux || freebsd || darwin`; depends on `syscall` and `pkg/errors`.
- Risks and edge cases: Casts and syscall field sizes vary by architecture; invalid or unsupported paths return raw syscall errors.
- Test signals: Covered by `stat_test.go` on matching platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/stat/stat_unix.go -->
