<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_windows.go -->
# sources/sync-backup/restic/internal/selfupdate/download_windows.go

## Purpose
Provides Windows self-update removal behavior for locked running binaries.

## Important APIs and Control Flow
`removeResticBinary` checks whether the target exists, removes an old `.bak` file if present, then renames the current executable to `<name>.bak` before replacement. Control flow handles missing targets as success and wraps rename failures with a clear error.

## State, Persistence, Dependencies, and Integration
Persistent state may include a `.bak` copy of the previous binary. It integrates with `extractToFile` before final `os.Rename`.

## Risks and Test Signals
Risks are stale backup cleanup failures and locked-file rename behavior. The general extraction test exercises overwrite, while Windows-specific behavior is mainly covered by platform execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/download_windows.go -->
